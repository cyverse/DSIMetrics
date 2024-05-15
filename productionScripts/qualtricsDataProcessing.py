#!/home/austinmedina/DataLabMetrtics/Metrics/bin/python
#The above header, allows the file to be independently run by Cron jobs
import pandas as pd
import requests
import time
import zipfile
import io
import logging
import psycopg2

def create_workshops_list(row):
    """
    This function will create a list of every index where the selected workshop isnt none. In the qualtrics survey, the workshops are listed
    chronologically. We can also pull the workshops from our database chronologically, so instead of perfectly matching names, we just match the index
    that the workshops occured.

    Key Arguments:
    row - Each row is one persons qualtrics response containing their first name, last name, email, netid, major, college, department, and workshops selected

    Example:
    The users selection looks like this: [Workshop 1, None, None, Workshop 4]
    The function will then return [0, 3]. 
    The indexes will be used in createRegistreeWorkshop
    """

    if pd.notnull(row.iloc[6]):
        return list(range(len(row) - 8))
    else:
        return [i for i, workshop in enumerate(row[7:-1], start=0) if pd.notnull(workshop)]

def getResponse(surveyId, conn, cur) :
    """
    Initiates the export for a qualtrics form to a csv.
    
    Key Arguments:
    surveyID -- The qualtricsID found on the qualtrics website. Serves as a unique identifier for each survey

    Return:
    Response -- The fileId that can be used to access the file
    """
    cur.execute("""SELECT ElementValue FROM programvariables 
                    WHERE ElementName = 'qualtrics_api_token'
                """)
    tokenList = cur.fetchone()
    conn.commit()
    apiKey = tokenList[0]

    url = f"https://iad1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses"
    payload = {"format": "csv",
               "useLabels": True}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-TOKEN": f"{apiKey}"
    }
    
    response = (requests.post(url, json=payload, headers=headers)).json()

    if (response["result"]["progressId"] and (response["meta"]["httpStatus"] == "200 - OK")):
        httpStatus = "200 - OK"
        status= ""
        percentComplete = ""
        exportProgressId = response["result"]["progressId"]
        logging.info("File Export Started")
        logging.info("---")
        url = f"https://iad1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses/{exportProgressId}"
        while ((httpStatus == "200 - OK") and (percentComplete != 100) and (status != "failed")):
            headers = {
                "Accept": "application/json",
                "X-API-TOKEN": f"{apiKey}"
            }

            response = (requests.get(url, headers=headers)).json()

            httpStatus = response["meta"]["httpStatus"]
            status = response["result"]["status"]
            percentComplete = response["result"]["percentComplete"]
            logging.info(f"File Export {percentComplete}% complete")
            logging.info("---")
            time.sleep(2)

        if((percentComplete == 100) and (status == "complete")):
            logging.info("File Export Complete")
            logging.info("---")
            fileId = response["result"]["fileId"]
            url = f"https://iad1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses/{fileId}/file"
            headers = {
                "Accept": "application/octet-stream, application/json",
                "X-API-TOKEN": f"{apiKey}"
            }
            response = requests.get(url, headers=headers)
            if (response.status_code == 200):
                logging.info("File successfully retrieved!")
                return response
            else:
                logging.info(f"Failed to retrieve file. Error: {response.status_code}")
                logging.info("---------------------------------------")
                return None
        else:
            logging.info(f'Export failed:\nhttpStatus: {response["meta"]["httpStatus"]}\npercentComplete: {response["result"]["percentComplete"]}\nStatus: {response["result"]["status"]}')

            return None
    else:
        logging.info(f"Export unable to start. Error: {response.status_code}")
        return None

def processFile(file):
    """
    Download and process the csv for a specific qualtrics form.
    
    Keyword Arguments:
    file -- The response from getResponse() which returns the bytestream for a file

    Return:
    UA_Filtered -- A pandas dataframe containing students who answered 'Yes' to UA Affiliated in the Qualtrics survey
    nonUA_Filtered -- A pandas dataframe containing students who answered 'No' to UA Affiliated in the Qualtrics survey

    Description:
    Decodes the byte stream from the response, and turns it into a csv file. 
    Pandas is used to parse the csv file and split the values into UA and nonUA dataframes
    """
    try:
        with zipfile.ZipFile(io.BytesIO(file.content)) as z:
            z.extractall('/home/austinmedina/DataLabMetrtics/productionScripts/qualtricsCSVs/')
            fileName = z.namelist()
            rawSurvey = pd.read_csv('/home/austinmedina/DataLabMetrtics/productionScripts/qualtricsCSVs/' + fileName[0])
    except(zipfile.BadZipFile, IndexError, pd.errors.EmptyDataError, pd.errors.ParserError, KeyError) as e:
        logging.critical(f"Error processing file: {e}")
        return None, None

    logging.info(f"File {fileName} extracted successfully")
    logging.info("---")

    filteredSurvey = rawSurvey[rawSurvey.columns[18:]]
    filteredSurvey = filteredSurvey.drop([0,1])
    filteredSurvey.reset_index(inplace=True, drop=True)
    filteredSurvey['Workshops'] = filteredSurvey.apply(create_workshops_list, axis=1)
    filteredSurvey.drop(columns = filteredSurvey.columns[6:-2], inplace=True)
    filteredSurvey["Recontact"] = filteredSurvey["Recontact"].fillna('No').map({'Yes': True, 'No': False})
    UA = filteredSurvey.dropna(subset=["UAEmail"])
    nonUA = filteredSurvey.dropna(subset=["NonUAEmail"])

    UA = UA.reset_index(drop=True)
    nonUA = nonUA.reset_index(drop=True)

    UA_Filtered = UA[["UAEmail", "FirstName", "LastName", "Workshops", "Series", "Recontact"]]
    nonUA_Filtered = nonUA[["NonUAEmail", "FirstName", "LastName", "Organization", "Workshops", "Series", "Recontact"]]

    logging.info(f"File {fileName} processed successfully")
    logging.info("---------------------------------------")

    return UA_Filtered, nonUA_Filtered

def createRegistreeWorkshop(regID, seriesID, row, conn, cur):
    """
    Inserts a entry into the junction table linking a registree to each workshop they registred for

    Key Arguments:
    regID - The hashed ID for each user based on their email
    seriesID - The ID for the series associated with the currently processed qualtrics form
    row - Each row is one persons qualtrics response containing their first name, last name, email, netid, major, college, department, series, and workshops selected
    Conn - The connection to the Postgres database
    Cur - The cursor to the Postgres database

    Returns:
    Returns nothing, but will update the Postgres database
    """
    cur.execute("""
                SELECT workshopID FROM workshops WHERE seriesID = %s
                ORDER BY workshopDate
                """, (seriesID,))
    conn.commit()

    workshops = cur.fetchall()

    #This is where the return of the function create_woirkshop_list() is used. row.loc['Workshops'] will return the example list [0, 3]. 
    #We will then fetch the workshopIDs for the 0th and 3rd element returned from our select workshopID query.
    workshopsToAdd = [workshops[i][0] for i in row.loc['Workshops']]

    for workshopID in workshopsToAdd:
        cur.execute("""
                        INSERT INTO registreeworkshops (RegID, WorkshopID, Registered)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (regID, workshopID, True))
        conn.commit()

def uploadRegistrees(UA, seriesID, conn, cur):
    """
    Uploads each registree into the database or updates their information if they are already in the system

    Key Arguments:
    UA - A pandas dataframe containing all participant information from the qualtrics forms
    seriesID - The ID for the series associated with the currently processed qualtrics form
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database

    Return:
    N/A

    Description:
    Loops through each row of the dataframe, i.e. for each person, and inserts them into the database. Next it will call the createRegistreeWorkshop function which will officially register
    the participant for each workshop in our system.
    """
    for _, row in UA.iterrows():
        #Call my custom function hash which will create a hash from the Email
        cur.callproc('hashRegistree', (row.iloc[3],))
        hashedNum = cur.fetchone()[0]

        cur.execute("""
                    INSERT INTO registreeInfo (RegID, FirstName, LastName, NetID, Email, College, Department, Major, Recontact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (RegID) DO UPDATE
                    SET College = excluded.College, Department = excluded.Department, Major = excluded.Major, Recontact = excluded.Recontact;
                    """, (hashedNum, row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4], row.iloc[5], row.iloc[6], row.iloc[8]))
        conn.commit()

        createRegistreeWorkshop(hashedNum, seriesID, row, conn, cur)    

def processAllQualtrics(conn, cur):
    """
    Fetches all active series and processes their qualtrics forms

    Key Arguments:
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Returns:
    Returns nothing. The function serves as the main functionality for the script

    Description:
    An SQL query is called to find all series and their qualtrics IDs 
    """
    cur.execute("""
                SELECT QualtricsID, SeriesID FROM Series
                WHERE StartDate <= now()::date AND EndDate >= now()::date;
                """)
    seriesList = cur.fetchall()
    conn.commit()

    for series in seriesList:
        UA = pd.DataFrame()
        nonUA = pd.DataFrame()

        logging.info(f"Starting export for surveyId: {series[0]}")
        logging.info("------------------------------------------------")
        file = getResponse(series[0], conn, cur)
        logging.info("------------------------------------------------\n")

        logging.info(f"Starting processing for surveyId: {series[0]}")
        logging.info("------------------------------------------------")
        UA, nonUA = processFile(file)

        logging.info(f"Survey {series[0]} Complete!")
        logging.info("------------------------------------------------\n")

        UA['NetID'] = None
        UA['College'] = None
        UA['Department'] = None
        UA['Major'] = None
        UA = UA[['FirstName', 'LastName', 'NetID', 'UAEmail', 'College', 'Department', 'Major', 'Workshops', 'Recontact']]
        #Once available, run the NetID system
        uploadRegistrees(UA, series[1], conn, cur)

        nonUA['Department'] = None
        nonUA['Major'] = None
        nonUA['NetID'] = None
        nonUA.columns = ['NonUAEmail', 'FirstName', 'LastName', 'College', 'Workshops', 'Reconnect', 'Department', 'Major', 'NetID']
        nonUA = nonUA[['FirstName', 'LastName', 'NetID', 'NonUAEmail', 'College', 'Department', 'Major', 'Workshops', 'Reconnect']]
        uploadRegistrees(nonUA, series[1], conn, cur)

if __name__ == '__main__':
    """
    The main function for this script configures logging and opens the connection the database.
    """
    conn = psycopg2.connect(database = "DataLab", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "",
                            port = 5432)

    cur = conn.cursor()

    logging.basicConfig(filename='/home/austinmedina/DataLabMetrtics/logging/qualtricsLogging.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.FileHandler('/home/austinmedina/DataLabMetrtics/logging/qualtricsLogging.log')
    logging.info("Starting qualtrics check and upload.")

    processAllQualtrics(conn, cur)
    logging.info("Finished qualtrics check and upload.")