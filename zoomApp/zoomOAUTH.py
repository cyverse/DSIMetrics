#!/home/austinmedina/DataLabMetrtics/Metrics/bin/python
from flask import Flask, render_template, request, url_for, redirect, session, flash
import requests
import base64
import psycopg2
import logging
from secrets import secret_key

logging.basicConfig(filename = '/home/austinmedina/DataLabMetrtics/logging/ZoomFlaskAppLogging.log', level=logging.DEBUG)

"""
When this python script is run, it will start up a flask server which is connected via HAProxy to cerberus.cyverse.org. This web server is
responsible for gathering access and refresh tokens for zoom from each user. The server will then allow the user to enter in the meeting IDs
they wish the system to pull participants for.
"""
app = Flask(__name__)

app.secret_key = secret_key

"""
Main endpoint that will load credentials.html. This contains a button that will redicrect the user to the zoom app and ask for authorization
"""
@app.route('/')
def credentials():
    return render_template('credentials.html')

"""
Once the user is done authorizing zoom, they will be returned to this endpoint. This endpoint uses their authorization token to request an access token
The access token is what is actually needed to fetch the participant info. The end point saves the refresh token to a cookie to be inserted into the
system later with each meetingID. The refresh token allows you to fetch a new access token since the access tokens expire.
"""
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
    tokenList = cur.fetchone()
    client_id = tokenList[0]

    cur.execute("""SELECT ElementValue FROM programvariables WHERE ElementName = 'zoom_client_secret'""")
    tokenList = cur.fetchone()
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
    app.logger.info(re)
    session['refresh_token'] = re['refresh_token']
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for("getMeetingID"))

"""
The user is automatically directed to this page after their refresh key has been saved. The page prompts the user to enter in meeting IDs for
zooms they wish to get participants for. Everytime the users posts a meetingID, the script will insert the refresh key and meeting ID into a table
"""
@app.route('/getMeetingID', methods=["GET", "POST"])
def getMeetingID():
    if request.method == "POST":
        zoomID = request.form.get("meetingID")

        if not zoomID:
            flash('Zoom Meeting ID is required!', 'error')
            return redirect(url_for('getMeetingID'))
        else:
            conn = psycopg2.connect(database = "DataLab", 
                                    user = "postgres", 
                                    host= 'localhost',
                                    password = "",
                                    port = 5432)
            cur = conn.cursor()

            cur.execute("""
                        INSERT INTO ZoomRefreshTokens (ZoomMeetingID, RefreshToken) 
                        VALUES (%s, %s)
                        ON CONFLICT (ZoomMeetingID) DO UPDATE
                        SET RefreshToken = EXCLUDED.RefreshToken
                        """, (zoomID, session['refresh_token']))
            conn.commit()
            cur.close()
            conn.close()

            flash(f'Successfully entered Meeting ID: {zoomID}', 'success')
            return redirect(url_for('getMeetingID'))
    
    return render_template('zoomIDForm.html')

if __name__ == '__main__':
  app.run()