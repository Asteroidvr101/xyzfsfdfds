from flask import Flask, request, jsonify
import requests
from werkzeug.datastructures import headers


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
            ban_info = requestlog.json()
            if ban_info.get('errorCode') == 1002:
                ban_message = ban_info.get('errorMessage', "No ban message provided.")
                ban_details = ban_info.get('errorDetails', {})
                ban_expiration_key = next(iter(ban_details.keys()), None)
                ban_expiration_list = ban_details.get(ban_expiration_key, [])
                ban_expiration = ban_expiration_list[0] if len(ban_expiration_list) > 0 else "No expiration date provided."
                print(ban_info)
                return jsonify({
                    'BanMessage': ban_expiration_key,
                    'BanExpirationTime': ban_expiration
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
