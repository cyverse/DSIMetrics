import pandas as pd
from datetime import datetime, date, timedelta
import os
import numpy as np
import psycopg2

def uploadCheckIn(row, workshopID, conn, cur):
    #Fetch the supposed ID from the has function
    cur.callproc('hashRegistree', (row.iloc[2].lower(),))
    hashedNum = cur.fetchone()[0]
    conn.commit()

    #See if the RegID is in the databse already
    cur.execute("""SELECT RegID FROM registreeInfo WHERE RegID = %s""", (hashedNum,))
    match = cur.fetchall()
    conn.commit()

    if len(match) != 0:
        # Check if the participant is already associated with the current workshop
        cur.execute("""
            SELECT * FROM RegistreeWorkshops
            WHERE RegID = %s AND WorkshopId = %s
        """, (hashedNum, workshopID))
        workshop_match = cur.fetchall()

        if len(workshop_match) == 0:
            # Insert a new record for the workshop if not already present
            cur.execute("""
                INSERT INTO RegistreeWorkshops (RegID, WorkshopID, Registered, CheckedIn)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (hashedNum, workshopID, False, True))
            conn.commit()
        else:
            # Update the check-in status for the existing workshop entry
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
        print("Checked in by name: " + FirstName + " " + LastName)
    else:
        cur.execute("""INSERT INTO UnknownPeople (FirstName, LastName, WorkshopID)
                    VALUES(%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """, (FirstName, LastName, workshopID))
        conn.commit()
        print("Unknown Person Without Email: " + FirstName + " " + LastName)
    

def zoomProcess(conn, cur):
    for filename in os.listdir("./zoomCSVs_sp24"):
        if filename.endswith(".csv"):
            # Construct the full path to the CSV file
            filepath = os.path.join("./zoomCSVs_sp24", filename)
            
            # Read the CSV file into a pandas DataFrame, skipping the first 3 rows
            participants = pd.read_csv(filepath, usecols=['Name (Original Name)', 'User Email', 'Join Time', 'Leave Time'],
                           parse_dates=['Join Time', 'Leave Time'], 
                           date_format='%m/%d/%Y %I:%M:%S %p')


            name_split = participants['Name (Original Name)'].str.split(expand=True)
            participants['FirstName'] = name_split[0]
            participants['LastName'] = name_split.iloc[:, 1:].apply(lambda x: ' '.join(x.dropna()) if any(x.notna()) else None, axis=1)
            participants['User Email'] = participants['User Email'].replace({np.nan: None})

            participants = participants[['FirstName', 'LastName', 'User Email', 'Join Time', 'Leave Time']]
            participants.columns = ['FirstName', 'LastName', 'Email', 'JoinTime', 'LeaveTime']

            cur.execute("""
                        SELECT workshops.WorkshopID, series.StartTime, series.EndTime FROM workshops
                        JOIN series on workshops.SeriesID = series.SeriesID
                        WHERE workshops.Workshopdate = %s::date
                        """, (participants.loc[0]['JoinTime'],))
            workshopList = cur.fetchall()
            conn.commit()

            for workshop in workshopList:
                workshopStart = datetime.combine(date.today(), workshop[1])
                workshopEnd = datetime.combine(date.today(), workshop[2])

                for _, person in participants.iterrows():
                    participantStart = datetime.combine(date.today(), person['JoinTime'].time())
                    participantLeave = datetime.combine(date.today(), person['LeaveTime'].time())

                    join_difference = abs(participantStart - workshopStart)
                    leave_difference = abs(participantLeave - workshopEnd)

                    # Filter participants within 15 minutes of workshop start or end time
                    if (join_difference < timedelta(minutes=15)) or (leave_difference < timedelta(minutes=15)):
                        if person['Email']:
                            print("Checked in: " + str(person['Email']))
                            uploadCheckIn(person, workshop[0], conn, cur)
                        elif person['FirstName'] and person['LastName']:
                            uploadWithoutEmail(person['FirstName'], person['LastName'], workshop[0], conn, cur)

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

    
    zoomProcess(conn, cur)    

    cur.close()
    conn.close()
