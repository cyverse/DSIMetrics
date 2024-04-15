import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import json

def scrapeWorkshops(url, seriesName):
    response = requests.get(url)
    if (response.status_code == 200):
        soup = BeautifulSoup(response.content, "html.parser")
        
        #Finds all instances of a paragraph with the word 'Topic" in the header of the paragraph
        results = soup.find_all(lambda tag: tag.name == 'p' and any(text in tag.get_text() for text in ['Topic']))
        
        data = []

        if (len(results) != 0):
            spans = results[0].find_all('span')
            #error handler for if zero
            #Sometimes the header is disconnected from the main list so we need the next element
            if (len(spans) == 1):
                results = results[0].findNext('p')
                spans = results.find_all('span')
            else:
                #Remove the first element since its the header 'Topic"
                spans.pop(0)
            
            i = 0
            year = datetime.now().year

            while i < len(spans):
                temp = []
                text = spans[i].get_text().strip()

                #isName = re.findall(r'^[A-Za-z\s]+$', text) #Finds if a line contains just a name and no date

                #Checks if the next element is a 'c-mrkdwn__tab' and skips it if so
                try:
                    attrs = spans[i+1].attrs
                    if (len(attrs) != 0) and attrs["class"][0] == 'c-mrkdwn__tab':
                        i += 1
                except:
                    pass

                #Checks to see if the element is a date in the format mm/dd
                if re.findall(r'^\d{1,2}/\d{1,2}$', text):
                    date = text + '/' + str(year)
                    temp.append(datetime.strptime(date, '%m/%d/%Y'))
                    temp.append(spans[i+1].get_text().strip())
                    i += 1
                elif re.findall(r'^\d{1,2}/\d{1,2}:$', text):
                    date = text + '/' + str(year)
                    temp.append(datetime.strptime(date, '%m/%d/%Y:'))
                    temp.append(spans[i+1].get_text().strip())
                    i += 1
                elif re.findall(r'^\d{1,2}/\d{1,2}/\d{1,2}$', text):
                    temp.append(datetime.strptime(text, '%m/%d/%y'))
                    temp.append(spans[i+1].get_text().strip())
                    i += 1
                elif re.findall(r'^\d{1,2}/\d{1,2}/\d{1,2}:$', text):
                    temp.append(datetime.strptime(text, '%m/%d/%y:'))
                    temp.append(spans[i+1].get_text().strip())
                    i += 1
                #If neither of those, then the date and name are in the same span and need to be split
                else:
                    split_content = text.split(maxsplit=1)
                    #Checks the format of the date mm/dd
                    if re.findall(r'^\d{1,2}/\d{1,2}$', split_content[0]): 
                        date = split_content[0] + '/' + str(year)
                        temp.append(datetime.strptime(date, '%m/%d/%Y'))
                    elif re.findall(r'^\d{1,2}/\d{1,2}:$', split_content[0]): 
                        date = split_content[0] + '/' + str(year)
                        temp.append(datetime.strptime(date, '%m/%d/%Y:'))
                    #Checks to see if the format of the date is mm/dd/yy
                    elif re.findall(r'^\d{1,2}/\d{1,2}/\d{1,2}$', split_content[0]):
                        temp.append(datetime.strptime(split_content[0], '%m/%d/%y'))
                    elif re.findall(r'^\d{1,2}/\d{1,2}/\d{1,2}:$', split_content[0]):
                        temp.append(datetime.strptime(split_content[0], '%m/%d/%y:'))

                    try:
                        temp.append(split_content[1])
                    except IndexError:
                        temp.append(None)
                    
                data.append(temp)
                i += 1
        else:
            #check to see i retruns something
            results = soup.find(lambda tag: tag.name == 'h2' and any(text in tag.get_text() for text in ['When'])).findNext('div')
            results.contents.pop(0)
            data = []
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
    
def uploadSeriesZoomID(id, conn, cur):
    cur.execute("""
        INSERT INTO ZoomRefreshTokens (ZoomMeetingID)
        VALUES (%s)
        ON CONFLICT DO NOTHING;
    """, (id,))
    conn.commit()

def uploadWorkshops(workshops, conn, cur):
    for _, row in workshops.iterrows():
        cur.execute("""
            INSERT INTO workshops (SeriesID, WorkshopName, WorkshopDate)
            VALUES (%s, %s, %s);
        """, tuple(row))
        conn.commit()

    return
    
def initializeWorkshops(series, conn, cur):
    seriesDict = json.loads(series)
    uploadSeriesZoomID(seriesDict['zoommeetingid'], conn, cur)
    
    workshops = pd.DataFrame()

    workshops = scrapeWorkshops(seriesDict["seriesurl"], seriesDict["seriesname"])
    workshops['SeriesID'] = seriesDict['seriesid']

    workshops = workshops[['SeriesID', 'WorkshopName', 'Date']]
    uploadWorkshops(workshops, conn, cur)

    