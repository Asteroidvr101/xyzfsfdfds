import requests
from flask import Flask, jsonify, request

class GameInfo:
    def __init__(self):
        self.TitleId: str = "7AF94"
        self.SecretKey: str = "GBIPB74594RF9UDYHIAKASEJ1WG66KWWF4FAPKJK1WYZCC94S7"

    def get_auth_headers(self):
        return {
            "X-SecretKey": self.SecretKey,
            "Content-Type": "application/json"
        }

settings = GameInfo()
app = Flask(__name__)

@app.route('/')
def index():
    return 'i Think The Backend Is Working Fucker'

@app.route('/api/PlayFabAuthentication', methods=['POST', 'GET'])
def playfab_authentication():
    sigma = request.get_json()
    oculusid = sigma.get('OculusId')
    requestlogin = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
        headers=settings.get_auth_headers(),
        json= {
            "CustomId": "OCULUS" + oculusid,
            "CreateAccount": True
        }
    )

    if requestlogin.status_code == 200:
        skibidi = requestlogin.json()
        return jsonify({
            "PlayFabId": skibidi["data"]["PlayFabId"],
            "SessionTicket": skibidi["data"]["SessionTicket"],
            "EntityToken": skibidi["data"]["EntityToken"]["EntityToken"],
            "EntityId": skibidi["data"]["EntityToken"]["Entity"]["Id"],
            "EntityType": skibidi["data"]["EntityToken"]["Entity"]["Type"],
        })
    else:
        banshit = requestlogin.json()
        if banshit.get("errorCode") == 1002:
            banmessage = banshit.get("errorMessage")
            bandetails = banshit.get("errorDetails", "message")
            banexpirekey = bandetails(next(iter(bandetails.keys())), None)
            banexpirelist = banshit.get(banexpirekey(), [])
            banexpiretime = banexpirelist[0] if len(banexpirelist) > 0 else "Infinite"

            return jsonify({
                "BanMessage": banmessage,
                "BanExpireTime": banexpiretime
            }), 403

@app.route('/api/TitleData', methods=['GET', 'POST'])
def titledata():
    requestdata = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.get_auth_headers(),
    )

    if requestdata.status_code == 200:
        return jsonify(requestdata.json())


@app.route('/api/CachePlayFabId', methods=['POST', 'GET'])
def cacheplayfabid():
    return "Niggas In Parise", 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
