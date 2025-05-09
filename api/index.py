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
    customid = data.get("CustomId")
    if 'UnityPlayer' not in request.headers.get('User-Agent', ''):
        return jsonify({
            "BanMessage": "Invalid User-Agent",
            "BanExpirationTime": "Infinite"
        }), 403
    if customid.startswith("OCULUS"):
        return jsonify({
            "BanMessage": "Invalid CustomId",
            "BanExpirationTime": "Infinite"
        }), 403
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
            "PlayFabId":
            playerdata["data"]["PlayFabId"],
            "SessionTicket":
            playerdata["data"]["SessionTicket"],
            "EntityToken":
            playerdata["data"]["EntityToken"]["EntityToken"],
            "EntityId":
            playerdata["data"]["EntityToken"]["Entity"]["Id"],
            "EntityType":
            playerdata["data"]["EntityToken"]["Entity"]["Type"],
        }), 200
    else:
        if requestlog.status_code == 403:
            bannywanny = requestlog.json()
            if bannywanny.get("errorCode") == 1002:
                banmessage = bannywanny.get("errorMessage", "No Message Found")
                bandetails = bannywanny.get("errorDetails", {})
                banexpirekey = next(iter(bandetails.keys()), None)
                banexpirelist = bannywanny.get(banexpirekey, [])
                banexpire = banexpirelist[0] if len(
                    banexpirelist) > 0 else "Infinite"
                print(bannywanny)
                return jsonify({
                    "BanMessage": banexpirekey,
                    "BanExpirationTime": banexpire
                }), 403
            else:
                errormessage = bannywanny.get("errorMessage",
                                              "No Message Found")
                return jsonify({
                    "Error": "PlayFabError",
                    "Message": errormessage
                }), 403
        else:
            errorinfo = requestlog.json()
            errormessages = errorinfo.get("errorMessage", "An Error Occurred")
            return jsonify({
                "Error": "PlayFabError",
                "Message": errormessages
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
