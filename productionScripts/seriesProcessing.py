import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import json
import logging

def scrapeWorkshops(url, seriesName):
    """
    If a series URL was provided when creating the workshop this function will create workshop entries based on the calandar link

    Key Arguments:
    url - The url for the series, ex: https://datascience.arizona.edu/events/navigating-world-data-engineering
    seriesName - The name of the new series being created

    Description:
    The function will fetch the html for the specific url. Next it uses beautiful soup to parse the html, looking for the 'When' header, which provides us all the dates the workshop occurs.
    Then the function will find each date within the When heading and convert it to datetime by trying the two possible datetime types. It will then append the date to the seriesName, refered
    to as 'WorkshopName'. The function defaults the workshop name to the seriesName since the workshop names are constantly changing. These can be changed in the workshops page on Budibase.
    If the function cannot find the URL or throws an error, it will return none, and no workshops will be created for the series and they will need to be created manually.
    """
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

def uploadWorkshops(workshops, conn, cur):
    """
    For each workshop in the list found from webscraping, a new workshop entry will be created

    Key Arguments:
    workshops - The list of workshop dates and associated names for a specific series
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 
    """
    for _, row in workshops.iterrows():
        cur.execute("""
            INSERT INTO workshops (SeriesID, WorkshopName, WorkshopDate)
            VALUES (%s, %s, %s);
        """, tuple(row))
        conn.commit()

    return
    
def initializeWorkshops(series, conn, cur):
    """
    Function called from the series listener to process the notification payload for a new series

    Key Arguments:
    series - The notification payload containing a string in json format with information on the new series
    conn - The connection to the Postgres database
    cur - The cursor to the Postgres database 

    Description:
    The listener passes through the notification payload. This script then converts it to JSON for easy usability. The function then scrapes each of the workshops and if workshops are found
    the script will upload them to the database.
    """
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

    