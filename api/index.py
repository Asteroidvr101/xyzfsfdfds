import datetime
from flask import Flask, request, jsonify
import requests
from werkzeug.datastructures import headers
from datetime import datetime, timedelta



class GameSettings:

    def __init__(self):
        self.TitleId: str = "7AF94"
        self.SecretKey: str = "GBIPB74594RF9UDYHIAKASEJ1WG66KWWF4FAPKJK1WYZCC94S7"

    def auth_headers(self):
        return {
            "Content-Type": "application/json",
            "X-SecretKey": settings.SecretKey
        }


settings = GameSettings()
app = Flask(__name__)


@app.route('/')
def index():
    return 'I Think The Backend Is Working'



@app.route('/api/PlayFabAuthentication', methods=['POST', 'GET'])
def playfab_auth():
    data = request.get_json()
    oculusid = data.get("OculusId")
    requestlog = requests.post(
        url=
        f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
        headers=settings.auth_headers(),
        json={
            "CustomId": "OCULUS" + oculusid,
            "CreateAccount": True
        })
    if requestlog.status_code == 200:
        playerdata = requestlog.json()
        return jsonify({
            "PlayFabId": playerdata["data"]["PlayFabId"],
            "SessionTicket": playerdata["data"]["SessionTicket"],
            "EntityToken": playerdata["data"]["EntityToken"]["EntityToken"],
            "EntityId": playerdata["data"]["EntityToken"]["Entity"]["Id"],
            "EntityType": playerdata["data"]["EntityToken"]["Entity"]["Type"],
        }), 200
    else:
        if requestlog.status_code == 403:
            banshitty = requestlog.json()
            if banshitty.get('errorCode') == 1002:
                banmessage = banshitty.get('errorMessage', 'No Message Found')
                bandetails = banshitty.get('errorDetails', {})
                banexpkey = next(iter(bandetails.keys()), None)
                banexplist = bandetails.get(banexpkey, [])
                banexp = banexplist[0] if len(banexplist) > 0 else 'Infinite'
                print (banshitty)
                return jsonify({
                    "BanMessage": banexpkey,
                    "BanExpirationTime": banexp
                }), 403


@app.route('/api/CachePlayFabId', methods=['POST', 'GET'])
def cache_playfab_id():
    return 'HAHA', 200

itemname1 = "LMAJD."
itemname2 = "LBACP."
itemname3 = "LMAKH."

@app.route('/api/TitleData', methods=['GET', 'POST'])
def title_data():
    today = datetime.utcnow().date()
    startweek = today - timedelta(days=today.weekday())
    endweek = startweek + timedelta(days=6)

    data = {
        "TOTD": [
                {
                    "PedestalID": "CosmeticStand1",
                    "ItemName": itemname1,
                    "StartTimeUTC": startweek.strftime("%Y-%m-%dT00:00:00Z"),
                    "EndTimeUTC": endweek.strftime("%Y-%m-%dT23:59:59Z")
                },
                {
                    "PedestalID": "CosmeticStand2",
                    "ItemName": itemname2,
                    "StartTimeUTC": startweek.strftime("%Y-%m-%dT00:00:00Z"),
                    "EndTimeUTC": endweek.strftime("%Y-%m-%dT23:59:59Z")
                },
                {
                    "PedestalID": "CosmeticStand3",
                    "ItemName": itemname3,
                    "StartTimeUTC": startweek.strftime("%Y-%m-%dT00:00:00Z"),
                    "EndTimeUTC": endweek.strftime("%Y-%m-%dT23:59:59Z")
                }
            ]
        }

    return jsonify(data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
