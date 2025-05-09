from flask import Flask, request, jsonify
import requests
from werkzeug.datastructures import headers


class GameSettings:

    def __init__(self):
        self.TitleId: str = "7AF94"
        self.SecretKey: str = "GBIPB74594RF9UDYHIAKASEJ1WG66KWWF4FAPKJK1WYZCC94S7"
        self.WebhookUrl: str = "https://discord.com/api/webhooks/1360361457820373206/GmmIFUI8NOQ9yQBovEfFfNWASr4CaF8UEBhRAHtBpw8rfQWS4qKbtPKpjGwESYbRsoqq"

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

pollers = [
    {
        "PollId": 3,
        "Question": "Do You Like This Backend?",
        "VoteOptions": ["YES", "NO"],
        "VoteCount": [],
        "PredictionCount": [],
        "StartTime": "2025-05-09T00:00:00Z",
        "EndTime": "2025-05-10T00:00:00Z",
        "isActive": True
    }
]


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


@app.route('/api/TitleData', methods=['GET', 'POST'])
def title_data():
    requestdata = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.auth_headers())

    if requestdata.status_code == 200:
        return jsonify(requestdata.json())


@app.route('/api/FetchPoll', methods=['GET', 'POST'])
def fetch_poll():
    return jsonify(pollers), 200


@app.route('/api/Vote', methods=['GET', 'POST'])
def vote():
    data = request.get_json()
    poll_id = data.get("PollId")
    optionindex = data.get("OptionIndex")
    isprediction = data.get("IsPrediction")
    playfabid = data.get("PlayFabId")
    sigma = next((poll for poll in pollers if poll["PollId"] == poll_id), None)

    if not sigma:
            return "Poll Not Found", 404
    if optionindex < 0 or optionindex >= len(sigma["voteOptions"]):
            return 'Invalid Vote Option', 400
        

    embed = {
        "embeds": [
            {
                "title": "New Vote",
                "description": f"Poll ID: {poll_id}\nOption: {sigma['VoteOptions'][optionindex]}\nIs Prediction: {isprediction}\nPlayFab ID: {playfabid}"
            }
        ]
    }

    requests.post(settings.WebhookUrl, json=embed)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
