#!/home/austinmedina/DataLabMetrtics/Metrics/bin/python
import psycopg2
import asyncio
from seriesProcessing import initializeWorkshops
import logging

def handle_notify():
    """
    Forever polls the postgres server for a notification. If the function recievies a notification it will log it and initilaize the workshops

    The notification is a list of the information from a new series. When a new series is entered in budibase it is uploaded to the postgres database.
    Upon insertion, postgres sends out a notification saying something was added to the database. Within the payload of the notification is the new series info in string format
    """
    conn.poll()
    for notify in conn.notifies:
        logging.info("THE FOLLOWING WAS CAUGHT: " + notify.payload)
        initializeWorkshops(notify.payload, conn, cur)
    conn.notifies.clear()

def listenNewSeries():
    """
    Creates an event loops that runs forever listening to the notification channel newSeries
    """
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur.execute(f"LISTEN newSeries;")

    loop = asyncio.get_event_loop()
    loop.add_reader(conn, handle_notify)
    loop.run_forever()

if __name__ == '__main__':
    """
    The main function for the listener. Configures logging
    """
    logging.basicConfig(filename='/home/austinmedina/DataLabMetrtics/logging/seriesListener.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.FileHandler('/home/austinmedina/DataLabMetrtics/logging/seriesListener.log')

    logging.info("STARTING SERIES INSERT LISTENER")
    print("STARTING SERIES INSERT LISTENER")

    conn = psycopg2.connect(database = "DataLab", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "",
                            port = 5432)
    cur = conn.cursor()
    listenNewSeries()
    