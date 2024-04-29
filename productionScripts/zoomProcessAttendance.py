#!/home/austinmedina/DataLabMetrtics/Metrics/bin/python

import requests
import base64
from datetime import datetime, timedelta, date, timezone
import pytz
import psycopg2
import pandas as pd
import logging  

def getRefreshToken(workshopID, conn, cur):    
    cur.execute("""SELECT RefreshToken FROM ZoomRefreshTokens 
                WHERE ZoomMeetingID = %s
                """, (workshopID,))
    tokenList = cur.fetchone()

    conn.commit()
    return tokenList[0]

def getAccessToken(refreshToken, zoomMeetingID, conn, cur):
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
    refreshToken = getRefreshToken(zoomMeetingID, conn, cur)
    accessToken = getAccessToken(refreshToken, zoomMeetingID, conn, cur)
    url = f'https://api.zoom.us/v2/past_meetings/{zoomMeetingID}/participants'

    headers = {
        'Authorization':f'Bearer {accessToken}',
        'page_size':'100'
    }

    response = requests.get(url, headers=headers)

    if (response.status_code == 200):
        people = (response.json())
        return people['participants']
    else:
        print(f'Error: {response.status_code}')
        return None
    
def uploadCheckIn(row, workshopID, conn, cur):

    #Fetch the supposed ID from the has function
    cur.callproc('hashRegistree', (row.iloc[3].lower(),))
    hashedNum = cur.fetchone()[0]
    conn.commit()

    #See if the RegID is in the databse already
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
    # Parse the UTC time string into a datetime object
    utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')

    # Define UTC timezone
    utc_timezone = pytz.timezone('UTC')

    # Convert the UTC time to Arizona time
    arizona_timezone = pytz.timezone('America/Phoenix')
    arizona_time = utc_timezone.localize(utc_time).astimezone(arizona_timezone)

    return arizona_time.time()

def are_dates_equal(arizona_date, utc_date_str):
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    arizona_to_utc_offset = timedelta(hours=7)  # Arizona is UTC-7
    arizona_date_utc = utc_date - arizona_to_utc_offset
    return arizona_date_utc.date() == utc_date.date()

def zoomProcess(conn, cur):
    cur.execute("""
                SELECT workshops.WorkshopID, workshops.SeriesID, series.ZoomMeetingID, series.StartTime, series.EndTime, workshops.WorkshopDate FROM workshops
                JOIN series on workshops.SeriesID = series.SeriesID
                WHERE workshops.Workshopdate = now()::date
                """)

    workshopList = cur.fetchall()
    conn.commit()

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
    
    
    cur.close()
    conn.close()
