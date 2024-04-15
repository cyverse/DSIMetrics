import psycopg2
import asyncio
from seriesProcessing import initializeWorkshops

def handle_notify():
    conn.poll()
    for notify in conn.notifies:
        print("THE FOLLOWING WAS CAUGHT: " + notify.payload)
        initializeWorkshops(notify.payload, conn, cur)
    conn.notifies.clear()

def listenNewSeries():
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur.execute(f"LISTEN newSeries;")

    loop = asyncio.get_event_loop()
    loop.add_reader(conn, handle_notify)
    loop.run_forever()

if __name__ == '__main__':
    conn = psycopg2.connect(database = "DataLab", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "",
                            port = 5432)
    cur = conn.cursor()
    listenNewSeries()
    