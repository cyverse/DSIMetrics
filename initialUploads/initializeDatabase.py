from initialWorkshop import initializeWorkshops
from initialGoogleCheckIn import initializeCheckIn
from InitialQualtricProcessing import initializeQualtrics
from initialZoomUpload import zoomProcess

import psycopg2

if __name__ == '__main__':
    print('INITIAL UPLOAD STARTED')
    conn = psycopg2.connect(database = "DataLab", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "",
                            port = 5432)

    cur = conn.cursor()

    with open("./postgreSQLScripts/tableInitialize.sql", 'r') as f:
        sql_script = f.read()

    cur.execute(sql_script)
    conn.commit()

    initializeWorkshops(conn, cur)

    initializeQualtrics(conn, cur)

    initializeCheckIn(conn, cur)

    zoomProcess(conn,cur)