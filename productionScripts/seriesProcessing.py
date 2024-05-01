import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import json
import logging

def scrapeWorkshops(url, seriesName):
    try:
        response = requests.get(url)
        if (response.status_code == 200):
            soup = BeautifulSoup(response.content, "html.parser")
            data = []
            #Finds all instances of a heading2 with the word 'When" in the header of the paragraph
            results = soup.find(lambda tag: tag.name == 'h2' and any(text in tag.get_text() for text in ['When'])).findNext('div')
            if (results != 0):
                results.contents.pop(0)
                
                for i in range(0, len(results.contents), 2):
                    temp = []
                    date = results.contents[i].get_text().strip().split(', ', maxsplit=1)[1]
                    for fmt in ('%b. %d, %Y', '%B %d, %Y'):
                        try:
                            temp.append(datetime.strptime(date, fmt))
                        except ValueError:
                            pass
                    temp.append(seriesName)
                    data.append(temp)
            return pd.DataFrame(data, columns = ['Date', 'WorkshopName'])
        else:
            return None
    except Exception as e:
        logging.info("Error handled gracefully. Continuing listening")
        return None

# Not needed, because the zoom insert needs to happen before the series insert which is handled by budibase 
# def uploadSeriesZoomID(id, conn, cur):
#     cur.execute("""
#         INSERT INTO ZoomRefreshTokens (ZoomMeetingID)
#         VALUES (%s)
#         ON CONFLICT DO NOTHING;
#     """, (id,))
#     conn.commit()

def uploadWorkshops(workshops, conn, cur):
    for _, row in workshops.iterrows():
        cur.execute("""
            INSERT INTO workshops (SeriesID, WorkshopName, WorkshopDate)
            VALUES (%s, %s, %s);
        """, tuple(row))
        conn.commit()

    return
    
def initializeWorkshops(series, conn, cur):
    logging.basicConfig(filename='/home/austinmedina/DataLabMetrtics/logging/seriesListener.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.FileHandler('/home/austinmedina/DataLabMetrtics/logging/seriesListener.log')

    seriesDict = json.loads(series)
    #uploadSeriesZoomID(seriesDict['zoommeetingid'], conn, cur)
    
    workshops = pd.DataFrame()

    workshops = scrapeWorkshops(seriesDict["seriesurl"], seriesDict["seriesname"])
    if (workshops):
        workshops['SeriesID'] = seriesDict['seriesid']

        workshops = workshops[['SeriesID', 'WorkshopName', 'Date']]
        uploadWorkshops(workshops, conn, cur)

    