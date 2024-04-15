import pandas as pd
import requests
import time
import zipfile
import io
import logging

def getResponse(surveyId, conn, cur):
    cur.execute("""SELECT ElementValue FROM programvariables WHERE ElementName = 'qualtrics_api_token'""")
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
                logging.critical(f"Failed to retrieve file. Error: {response.status_code}")
                logging.info("---------------------------------------")
                return None
        else:
            logging.critical(f'Export failed:\nhttpStatus: {response["meta"]["httpStatus"]}\npercentComplete: {response["result"]["percentComplete"]}\nStatus: {response["result"]["status"]}')

            return None
    else:
        logging.critical(f"Export unable to start. Error: {response.status_code}")
        return None
    
def processOldFile(file):
    try:
        with zipfile.ZipFile(io.BytesIO(file.content)) as z:
            z.extractall('/home/austinmedina/DataLabMetrtics/initialUploads/qualtricsCSVs/')
            fileName = z.namelist()
            rawSurvey = pd.read_csv('/home/austinmedina/DataLabMetrtics/initialUploads/qualtricsCSVs/' + fileName[0])
    except(zipfile.BadZipFile, IndexError, pd.errors.EmptyDataError, pd.errors.ParserError, KeyError) as e:
        logging.critical(f"Error processing file: {e}")
        return None, None

    logging.info(f"File {fileName} extracted successfully")
    logging.info("---")
    filteredSurvey = rawSurvey[rawSurvey.columns[18:26]]
    filteredSurvey.columns = ["Email", "FirstName", "LastName", "UAPosition", "UADeptOther", "UADept", "OtherDept", "Recontact"]
    filteredSurvey = filteredSurvey.drop([0,1])
    filteredSurvey = filteredSurvey.dropna(subset=["Email"])
    filteredSurvey = filteredSurvey.drop_duplicates(subset=["Email"])
    filteredSurvey["Series"] = fileName[0][12:-18]
    filteredSurvey["Recontact"] = filteredSurvey["Recontact"].fillna('No').map({'Yes': True, 'No': False})

    searchFor = ["Graduate student", "PostDoc", "Undergraduate student", "Faculty", "Staff"]

    UA = filteredSurvey.loc[(filteredSurvey["Email"].str.contains("arizona.edu")) | (filteredSurvey["UAPosition"].str.contains("|".join(searchFor)))]
    nonUA = pd.concat([filteredSurvey, UA]).drop_duplicates(keep=False)

    UA = UA.reset_index(drop=True)
    nonUA = nonUA.reset_index(drop=True)

    UA_Filtered = UA[["Email", "FirstName", "LastName", "Series", "Recontact"]]
    nonUA_Filtered = nonUA[["Email", "FirstName", "LastName", "UADeptOther", "OtherDept", "Series", "Recontact"]]

    logging.info(f"File {fileName} processed successfully")
    logging.info("---------------------------------------")

    return UA_Filtered, nonUA_Filtered

def processSpecialFile(file):
    try:
        with zipfile.ZipFile(io.BytesIO(file.content)) as z:
            z.extractall('/home/austinmedina/DataLabMetrtics/initialUploads/qualtricsCSVs/')
            fileName = z.namelist()
            rawSurvey = pd.read_csv('/home/austinmedina/DataLabMetrtics/initialUploads/qualtricsCSVs/' + fileName[0])
    except(zipfile.BadZipFile, IndexError, pd.errors.EmptyDataError, pd.errors.ParserError, KeyError) as e:
        logging.critical(f"Error processing file: {e}")
        return None, None

    logging.info(f"File {fileName} extracted successfully")
    logging.info("---")
    filteredSurvey = rawSurvey[rawSurvey.columns[17:26]]
    filteredSurvey.columns = ["FirstName", "LastName", "Email", "UAPosition", "UADeptOther", "UADept", "OtherDept", "Trash", "Recontact"]
    filteredSurvey = filteredSurvey.drop([0,1])
    filteredSurvey = filteredSurvey.dropna(subset=["Email"])
    filteredSurvey = filteredSurvey.drop_duplicates(subset=["Email"])
    filteredSurvey["Series"] = fileName[0][12:-4]
    filteredSurvey["Recontact"] = filteredSurvey["Recontact"].fillna('No').map({'Yes': True, 'No': False})

    searchFor = ["Graduate student", "PostDoc", "Undergraduate student", "Faculty", "Staff"]

    UA = filteredSurvey.loc[(filteredSurvey["Email"].str.contains("arizona.edu")) | (filteredSurvey["UAPosition"].str.contains("|".join(searchFor)))]
    nonUA = pd.concat([filteredSurvey, UA]).drop_duplicates(keep=False)

    UA = UA.reset_index(drop=True)
    nonUA = nonUA.reset_index(drop=True)

    UA_Filtered = UA[["Email", "FirstName", "LastName", "Series", "Recontact"]]
    nonUA_Filtered = nonUA[["Email", "FirstName", "LastName", "UADeptOther", "OtherDept", "Series", "Recontact"]]

    logging.info(f"File {fileName} processed successfully")
    logging.info("---------------------------------------")

    return UA_Filtered, nonUA_Filtered

def createRegistreeWorkshop(row, regID, conn, cur):
    cur.execute("""
                SELECT workshopID FROM workshops 
                LEFT JOIN series on series.seriesID = workshops.seriesID
                WHERE LOWER(series.seriesName) =  LOWER(%s)
                """, (row.iloc[7],))
    conn.commit()
    workshops = cur.fetchall()
    for ID in workshops:
        workshopID = ID[0]
        logging.info("Creating registree workshop for reg:" + row.iloc[3] + " workshopID:" + str(workshopID))
        cur.execute("""
                        INSERT INTO registreeworkshops (RegID, WorkshopID, Registered)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (regID, workshopID, True))
        conn.commit()

def uploadRegistrees(UA, conn, cur):
    for _, row in UA.iterrows():
        #Call my custom function hash which will create a hash from the Email
        cur.callproc('hashRegistree', (row.iloc[3].lower(),))
        hashedNum = cur.fetchone()[0]
        logging.info("Inserting row into registree:" + row.to_string())
        cur.execute("""
                    INSERT INTO registreeInfo (RegID, FirstName, LastName, NetID, Email, College, Department, Major, Recontact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (RegID) DO UPDATE
                    SET College = excluded.College, Department = excluded.Department, Major = excluded.Major, Recontact = excluded.Recontact;
                    """, (hashedNum, row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3].lower(), row.iloc[4], row.iloc[5], row.iloc[6], row.iloc[8]))
        conn.commit()

        createRegistreeWorkshop(row, hashedNum, conn, cur)    

def initializeQualtrics(conn, cur):
    logging.basicConfig(filename='/home/austinmedina/DataLabMetrtics/logging/qualtricsInitialLogging.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting, initial qualtrics upload.")
    seriesSurveyIDs = ["SV_5BjjU8Exp3GS2sS", "SV_9mLQalGxqyBb7mK", "SV_0fbG5COlxNj5phI", "SV_9TDHtSJnP6d32gS", "SV_exLckAyzfnUTKHc", "SV_9Rfr1WtU3kfMXjw"]

    UA = pd.DataFrame()
    nonUA = pd.DataFrame()

    for id in seriesSurveyIDs:
        logging.info(f"Starting export for surveyId: {id}")
        logging.info("------------------------------------------------")
        file = getResponse(id, conn, cur)
        logging.info("------------------------------------------------\n")

        logging.info(f"Starting processing for surveyId: {id}")
        logging.info("------------------------------------------------")
        tempUA, tempNonUA = processOldFile(file)
        UA = pd.concat([UA, tempUA])
        nonUA = pd.concat([nonUA, tempNonUA])

        logging.info(f"Survey {id} Complete!")
        logging.info("------------------------------------------------\n")

    id = "SV_9oGXsP5SKL9jNRA"
    logging.info(f"Starting export for surveyId: {id}")
    logging.info("------------------------------------------------")
    file = getResponse(id, conn, cur)
    logging.info(f"Starting processing for surveyId: {id}")
    tempUA, tempNonUA = processSpecialFile(file)
    UA = pd.concat([UA, tempUA])
    nonUA = pd.concat([nonUA, tempNonUA])
    logging.info(f"Survey {id} Complete!")
    logging.info("------------------------------------------------\n")

    UA['NetID'] = None
    UA['College'] = None
    UA['Department'] = None
    UA['Major'] = None
    UA = UA[['FirstName', 'LastName', 'NetID', 'Email', 'College', 'Department', 'Major', 'Series', 'Recontact']]

    nonUA['Major'] = None
    nonUA['NetID'] = None
    nonUA.columns = ['Email', 'FirstName', 'LastName', 'College', 'Department', 'Series', 'Recontact', 'Major', 'NetID', ]
    nonUA = nonUA[['FirstName', 'LastName', 'NetID', 'Email', 'College', 'Department', 'Major', 'Series', 'Recontact']]
    
    logging.info("Uploading UA registrees")
    uploadRegistrees(UA, conn, cur)

    logging.info("Uploading nonUA registrees")
    uploadRegistrees(nonUA, conn, cur)

