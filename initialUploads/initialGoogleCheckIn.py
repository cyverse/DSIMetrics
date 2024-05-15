import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta
import urllib.parse

def getData(conn, cur):
    
    lastDateRun = datetime.now() - timedelta(days = 180) #this variable will be the last time we ran the job
    query = f"SELECT * WHERE A > date '{lastDateRun.strftime('%Y-%m-%d')}'"
    queryEncoded = urllib.parse.quote(query)

    url = f'https://docs.google.com/spreadsheets/d/1nJ8iAE62v2qnl2r2xmYS62eUjfFHkphfny6eFIBmdW0/gviz/tq?tqx=out:csv&headers=1&tq={queryEncoded}'
    response = requests.get(url)
    content = response.content.decode()
    checkIn = pd.read_csv(StringIO(content))
    return checkIn

def getWorkshopID(time, conn, cur):
    #Fetch the series ID for the day of the week because this will determine the time frame we check in
    cur.execute("""SELECT DISTINCT SeriesID FROM workshops 
            WHERE workshopDate = %s::date
            """, (time,))
    match = cur.fetchall()
    conn.commit()

    #Check series to see if this day of a workshop is a day with 2 workshops back to back or not as that changes our time frame we can search in
    if (len(match) == 2):
        cur.execute("""SELECT startTime, endTime FROM series 
                WHERE seriesID = %s OR seriesID = %s 
                """, (match[0][0], match[1][0]))
        timeRange = cur.fetchall()
        conn.commit()
        startTime1 = datetime.combine(datetime(year=2000, month=1, day=1),timeRange[0][0] )
        endTime1 = datetime.combine(datetime(year=2000, month=1, day=1),timeRange[0][1])  
        startTime2 = datetime.combine(datetime(year=2000, month=1, day=1),timeRange[1][0])
        endTime2 = datetime.combine(datetime(year=2000, month=1, day=1),timeRange[1][1])

        #Workshop 1 ends right before Workshop 2 begins so the ranges cannot overlap
        if ((endTime1 - startTime2) < timedelta(minutes=1)):
            cur.execute("""SELECT seriesID FROM series 
                WHERE (seriesID = %s AND ((StartTime - interval '15 minutes') < time %s) AND (EndTime > time %s))
                OR (seriesID = %s AND (StartTime < time %s) AND ((EndTime + interval '15 minutes') > time %s))
                """, (match[0][0], time, time, match[1][0], time, time))
            
        #Workshop 2 ends right before Workshop 1 begins so the ranges cannot overlap
        elif((endTime2 - startTime1) < timedelta(minutes=1)):
            cur.execute("""SELECT seriesID FROM series 
                WHERE (seriesID = %s AND ((StartTime - interval '15 minutes') < time %s) AND (EndTime > time %s))
                OR (seriesID = %s AND (StartTime < time %s) AND ((EndTime + interval '15 minutes') > time %s))
                """, (match[1][0], time, time, match[0][0], time, time))
        
        #The workshops are just on the same day and do not collide
        else:
            cur.execute("""SELECT seriesID FROM series 
                WHERE ( (seriesID = %s) OR (seriesID = %s) ) AND ( ((StartTime - interval '15 minutes') < time %s) AND ((EndTime + interval '15 minutes') > time %s)) )
                """, (match[0][0], match[1][0], time, time))

        seriesID = cur.fetchall()
    #If this is the only workshop to happen on that day, then we can easily the workshopID for the workshop that happened on that day since there is only 1
    else:
        
        seriesID = match
    
    conn.commit()

    if (seriesID):
        cur.execute("""SELECT WorkshopID FROM workshops 
                    WHERE (WorkshopDate = date %s) AND SeriesID = %s
                    """, (time, seriesID[0][0]))
        workshopID = cur.fetchall()
        conn.commit()

        return workshopID[0][0]
    else:
        return -1

def uploadCheckIn(row, workshopID, conn, cur):

    #Fetch the supposed ID from the has function
    cur.callproc('hashRegistree', (row.iloc[2].lower(),))
    hashedNum = cur.fetchone()[0]
    conn.commit()

    #See if the RegID is in the databse already
    cur.execute("""SELECT RegID FROM registreeInfo WHERE RegID = %s""", (hashedNum,))
    match = cur.fetchall()
    conn.commit()

    #If the list isnt empty then a match was found so we will return the RegID
    if (len(match) != 0):
        cur.execute("""
                    UPDATE RegistreeWorkshops
                    SET CheckedIn = TRUE
                    WHERE RegID = %s AND WorkshopId = %s
                    """, (hashedNum, workshopID))
        conn.commit()
    #If the list is empty, there is no registrant matching the workshop so we will need to create an entry for them
    else:
        print("New registree created: " + str(hashedNum))
        #Create a registreeInfo entry for the person
        cur.execute("""
                    INSERT INTO registreeInfo (RegID, FirstName, LastName, NetID, Email, College, Department, Major, Recontact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """, (hashedNum, row.iloc[0], row.iloc[1], None, row.iloc[2].lower(), row.iloc[3], None, None, False))
        conn.commit()

        #Create an entry for the person and the specific workshop they attended
        cur.execute("""
                    INSERT INTO RegistreeWorkshops (RegID, WorkshopID, Registered, CheckedIn)
                    VALUES (%s, %s, %s, %s)
                    """, (hashedNum, workshopID, False, True))
        conn.commit()   

def initializeCheckIn(conn, cur):
    checkIn = getData(conn, cur)

    checkIn.columns = ['checkTime', 'Email', 'FirstName', 'LastName', 'Department']
    checkIn = checkIn[['FirstName', 'LastName', 'Email', 'Department', 'checkTime']]

    for _,row in checkIn.iterrows():
        workshopID = getWorkshopID(row.iloc[4], conn, cur)
        if (workshopID > 0):
            uploadCheckIn(row, workshopID, conn, cur) 