#!/home/austinmedina/DataLabMetrtics/Metrics/bin/python
#The above header, allows the file to be independently run by Cron jobs
import requests
import base64
from datetime import datetime, timedelta, date, timezone
import pytz
import psycopg2
import pandas as pd
import logging  

def getRefreshToken(zoomMeetingID, conn, cur):
    """
    Key Arguments:
    zoomMeetingID - The id associated with a zoom meeting that we will fetch a participant list for.
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Return:
    tokenList[0] - This is the refresh token needed to gain an access token

    Description:
    Fetches the refresh token for a specific zoom meeting ID, which is needed to fetch an access token.
    """
    cur.execute("""SELECT RefreshToken FROM ZoomRefreshTokens 
                WHERE ZoomMeetingID = %s
                """, (zoomMeetingID,))
    tokenList = cur.fetchone()

    conn.commit()
    return tokenList[0]

def getAccessToken(refreshToken, zoomMeetingID, conn, cur):
    """
    Key Arguments:
    refreshToken - The refresh token needed to get a new access token
    zoomMeetingID - The id associated with a zoom meeting that we will fetch a participant list for.
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Returns:
    accessToken - The token needed to make an API call to zoom for the participant list

    Description:
    Every meeting participant list can only be fetched with an access token. These access tokens however expire shortly after that are retrieved. The requests also return a refresh key which
    can be used to fetch a new access token. This function uses the refresh token to fetch a new access token, and stores the newly returned refresh token in the database.
    """
    cur.execute("""SELECT ElementValue FROM programvariables WHERE ElementName = 'zoom_client_id'""")
    tokenList = cur.fetchone()
    client_id = tokenList[0]

    cur.execute("""SELECT ElementValue FROM programvariables WHERE ElementName = 'zoom_client_secret'""")
    tokenList = cur.fetchone()
    client_secret = tokenList[0]
    conn.commit()

    auth_string = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    auth_header = f"Basic {encoded_auth}"

    data = {
        "refresh_token": refreshToken,
        "grant_type": "refresh_token",
    }

    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Send POST request
    response = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)

    re = response.json()
    accessToken = re['access_token']
    refreshToken = re['refresh_token']

    cur.execute("""UPDATE ZoomRefreshTokens 
                SET RefreshToken = %s 
                WHERE ZoomMeetingID = %s
                """, (refreshToken, zoomMeetingID))
    conn.commit()

    return accessToken

def getParticipants(zoomMeetingID, conn, cur):
    """
    Fetches a list of meeting participants for a specific Zoom meeting ID, handling pagination.

    Key Arguments:
    zoomMeetingID - The ID associated with a Zoom meeting to fetch a participant list.
    conn - The connection to the Postgres database.
    cur - The cursor to the Postgres database.

    Returns:
    all_participants - A list of all participants, their email, join time, and leave time across all pages.
    """
    refreshToken = getRefreshToken(zoomMeetingID, conn, cur)
    accessToken = getAccessToken(refreshToken, zoomMeetingID, conn, cur)
    url = f'https://api.zoom.us/v2/past_meetings/{zoomMeetingID}/participants'
    
    headers = {
        'Authorization': f'Bearer {accessToken}',
        'page_size': '100'
    }

    all_participants = []
    next_page_token = ''
    
    while True:
        params = {'next_page_token': next_page_token} if next_page_token else {}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            all_participants.extend(data.get('participants', []))
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break
        else:
            print(f'Error: {response.status_code}')
            break

    return all_participants
    
def uploadCheckIn(row, workshopID, conn, cur):
    """
    Checks in a user to a specific workshop if they are found in the particpants list

    Key Arguments:
    row - One person and their information from zoom such as email, join time, and leave time
    workshopID - The ID for the specific workshop they attended
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Return:
    No return, but updates the postgres database

    Description:
    The function takes in a participants information from the zoom api meeting participants list. Next a hash is created from the users email. We then find the participant in the database 
    or create a new entry. The users name is split into first and last, and then they are checked into the database by setting the checkedIn value to True.
    """
    #Fetch the supposed ID from the hash function
    cur.callproc('hashRegistree', (row.iloc[3].lower(),))
    hashedNum = cur.fetchone()[0]
    conn.commit()

    #See if the RegID is in the database already
    cur.execute("""SELECT RegID FROM registreeInfo WHERE RegID = %s""", (hashedNum,))
    match = cur.fetchall()
    conn.commit()

    #If the list isnt empty then a match was found so we will update their entry
    if (len(match) != 0):
        cur.execute("""
                    UPDATE RegistreeWorkshops
                    SET CheckedIn = TRUE
                    WHERE RegID = %s AND WorkshopId = %s
                    """, (hashedNum, workshopID))
        conn.commit()
    #If the list is empty, there is no registrant matching the workshop so we will need to create an entry for them
    else:
        logging.info("New registree created: " + str(hashedNum))
        #Create a registreeInfo entry for the person
        splitName = row.iloc[2]
        splitName = splitName.split(' ')
        splitName = [name.strip() for name in splitName]
        if (len(splitName) > 0):
            if (len(splitName) == 2):
                firstName = splitName[0]
                lastName = splitName[1]
            elif (len(splitName) > 2):
                firstName = splitName[0]
                lastName = ' '.join(splitName[1:])
            else:
                firstName = splitName[0]
                lastName = ''
        
            cur.execute("""
                        INSERT INTO registreeInfo (RegID, FirstName, LastName, NetID, Email, College, Department, Major, Recontact)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                        """, (hashedNum, firstName, lastName, None, row.iloc[3].lower(), None, None, None, False))
            conn.commit()

            #Create an entry for the person and the specific workshop they attended
            cur.execute("""
                        INSERT INTO RegistreeWorkshops (RegID, WorkshopID, Registered, CheckedIn)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """, (hashedNum, workshopID, False, True))
            conn.commit()   

def uploadWithoutEmail(FirstName, LastName, workshopID, conn, cur):
    """
    Checks in a user based on first and last name, otherwise adds them to unknown people if they cannot be found.

    Key Arguments:
    FirstName - The first name as listed by the zoom api
    LastName - The last name as listed by the zoom api
    workshopID - The ID for the specific workshop they attended
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Return:
    No return but upload the person to the database

    Description:
    If no email is available for the participant (i.e. they signed in as a guest on zoom) we will attemp to upload them using their first and last name. First the script trys to find an existing
    registree with that first and last name. If its found, the function checks them in. If they arent found they are added to the unknown people table.
    """
    FirstName = FirstName.lower().capitalize()
    LastName = LastName.lower().capitalize()
    cur.execute("""SELECT RegID FROM registreeInfo 
                WHERE FirstName = %s AND LastName = %s
                """, (FirstName, LastName))
    match = cur.fetchone()
    conn.commit()

    if (match):
        cur.execute("""
                    UPDATE RegistreeWorkshops
                    SET CheckedIn = TRUE
                    WHERE RegID = %s AND WorkshopId = %s
                    """, (match[0], workshopID))
        conn.commit()
        logging.info("Checked in by name: " + FirstName + " " + LastName)
    else:
        cur.execute("""INSERT INTO UnknownPeople (FirstName, LastName, WorkshopID)
                    VALUES(%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """, (FirstName, LastName, workshopID))
        conn.commit()
        if cur.rowcount == 1:
            logging.info("Unknown Person Without Email Added: " + FirstName + " " + LastName)
        else:
            logging.debug("Unknown Person Already in Database: " + FirstName + " " + LastName)

def convert_to_arizona_time(utc_time_str):
    """
    Converts a string time in UTC to arizona time

    Key Arguments:
    utc_time_str - A timestamp in string format in UTC

    Returns:
    arizona_time.time() - The time in arizona time in datetime format
    """
    # Parse the UTC time string into a datetime object
    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')

    # Define UTC timezone
    utc_timezone = pytz.timezone('UTC')

    # Convert the UTC time to Arizona time
    arizona_timezone = pytz.timezone('America/Phoenix')
    arizona_time = utc_timezone.localize(utc_time).astimezone(arizona_timezone)

    return arizona_time.time()

def are_dates_equal(arizona_date, utc_date_str):
    """
    Checks if the date in arizona time of a workshop, is equal to a date in utc when the utc date is converted to arizona time. Used to tell if a workshop occured on the same day as the zoom

    Key Arguments:
    arizona_date - The date of a workshop in Date format
    utc_date_str - The date of a zoom meeting in utc time as a string

    Return:
    True or False if the dates are equal or not
    """
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    arizona_to_utc_offset = timedelta(hours=7)  # Arizona is UTC-7
    arizona_date_utc = utc_date - arizona_to_utc_offset
    return arizona_date == arizona_date_utc.date()

def zoomProcess(conn, cur):
    """
    Matches the most recent zoom meeting with a workshop that occured today and that time, and checks in the participants

    Key Arguments:
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Description:
    The function first finds every workshop that occured today and their respective zoom meeting IDs. It then loops through every workshop and fetches the participants list for the associated
    zoom meeting ID. We then iterates through each person and compared their join and leave time with the start and end time of the workshop. If they joined and/or left within 15 minutes before 
    or after the start time or end time they will be checked in. Before checking in we verify they have an email, and if not we check them in without an email.
    """
    cur.execute("""
                SELECT workshops.WorkshopID, workshops.SeriesID, series.ZoomMeetingID, series.StartTime, series.EndTime, workshops.WorkshopDate FROM workshops
                JOIN series on workshops.SeriesID = series.SeriesID
                WHERE workshops.Workshopdate = now()::date;
                """)

    workshopList = cur.fetchall()
    conn.commit()
    logging.info("Workshops found:" + str(workshopList))

    today = date.today()

    for workshop in workshopList:
        participants = getParticipants(workshop[2], conn, cur) #ZoomMeetingID
        if participants:
            logging.info(participants)

            for person in participants:
                #Get the times the person was in the zoom
                userJoin = convert_to_arizona_time(person['join_time'])
                userLeave = convert_to_arizona_time(person['leave_time'])

                #Find the difference between when they joined and when they left. The combine is needed since you cannot subtract datetime.time objects
                joinDifference = abs(datetime.combine(today, userJoin) - datetime.combine(today, workshop[3]))
                leaveDifference = abs(datetime.combine(today, userLeave) - datetime.combine(today, workshop[4]))

                #Verify the dates are equal
                datesEqual = are_dates_equal(workshop[5], person['join_time'])

                #If they joined within 15 minutes of the start time or left within 15 minutes of the end time we will check them in
                if (( joinDifference < timedelta(minutes=15) ) or ( leaveDifference < timedelta(minutes=15) )) and (datesEqual):
                    if person['user_email']:
                        uploadCheckIn(pd.Series(person), workshop[0], conn, cur)
                        logging.info("Checked in: " + person['user_email'])
                        logging.info("--------------------------------------")
                    else:
                        splitName = person['name']
                        splitName = splitName.split(' ')
                        splitName = [name.strip() for name in splitName]
                        if (len(splitName) > 0):
                            if (len(splitName) == 2):
                                firstName = splitName[0]
                                lastName = splitName[1]
                            elif (len(splitName) > 2):
                                firstName = splitName[0]
                                lastName = ' '.join(splitName[1:])
                            else:
                                firstName = splitName[0]
                                lastName = ''

                            uploadWithoutEmail(firstName, lastName, workshop[0], conn, cur)
                            logging.info("--------------------------------------")
                        

if __name__ == '__main__':
    """
    The main function for the script. Configures logging and opens the connection to the database.
    """
    conn = psycopg2.connect(database = "DataLab", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "",
                            port = 5432)

    cur = conn.cursor()

    logging.basicConfig(filename='/home/austinmedina/DataLabMetrtics/logging/zoomLogging.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.FileHandler('/home/austinmedina/DataLabMetrtics/logging/zoomLogging.log')

    logging.info("STARTING ZOOM CHECK IN PROCESS")
    logging.info("--------------------------------------")
    zoomProcess(conn, cur)
    logging.info("--------------------------------------")
    logging.info("ENDING ZOOM CHECK IN PROCESS")
    logging.info(" ")
    
    cur.close()
    conn.close()
