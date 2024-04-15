from flask import Flask, render_template, request
import requests
import base64
import psycopg2
import logging

#logging.basicConfig(filename = 'logging.log', level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def credentials():
    return render_template('credentials.html')

@app.route('/getAccess')
def getAccess():
    q = request.args.to_dict()
    auth_code = q['code']

    conn = psycopg2.connect(database = "DataLab", 
                            user = "postgres", 
                            host= 'localhost',
                            password = "",
                            port = 5432)
    cur = conn.cursor()
    cur.execute("""SELECT ElementValue FROM programvariables WHERE ElementName = 'zoom_client_id'""")
    tokenList = cur.fetchall()
    client_id = tokenList[0]

    cur.execute("""SELECT ElementValue FROM programvariables WHERE ElementName = 'zoom_client_secret'""")
    tokenList = cur.fetchall()
    client_secret = tokenList[0]
    conn.commit()

    auth_string = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    auth_header = f"Basic {encoded_auth}"

    data = {
      "code": auth_code,
      "grant_type": "authorization_code",
      "redirect_uri": "https://cerberus.cyverse.org/getAccess",
    }

    headers = {
      "Authorization": auth_header,
      "Content-Type": "application/x-www-form-urlencoded"
    }

    # Send POST request
    response = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)

    re = response.json()
    app.logger.debug(re)
    refreshToken = re['refresh_token']

    updateString = f"UPDATE programvariables SET ElementValue = '{refreshToken}' WHERE ElementName = 'refresh_token';"
    cur.execute(updateString)
    conn.commit()
    cur.close()
    conn.close()
    
    return "<h1>DONE!<h1>"

if __name__ == '__main__':
  app.run()