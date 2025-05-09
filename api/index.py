from flask import Flask, request, jsonify
import requests

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
def playfab_authentication():
    data = request.get_json()
    oculusid = data.get('OculusId')
    requestlogin = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
        headers=settings.auth_headers(),
        json={
            "CustomId": "OCULUS" + oculusid,
            "CreateAccount": True
        },
    )

    if requestlogin.status_code == 200:
        skibdata = requestlogin.json()
        return jsonify({
            "PlayFabId": skibdata["data"]["PlayFabId"],
            "SessionTicket": skibdata["data"]["SessionTicket"],
            "EntityToken": skibdata["data"]["EntityToken"]["EntityToken"],
            "EntityId": skibdata["data"]["EntityToken"]["Entity"]["Id"],
            "EntityType": skibdata["data"]["EntityToken"]["Entity"]["Type"],
        })
    else:
        if requestlogin.status_code == 403:
            bannywanny = requestlogin.json()
            if bannywanny["errorCode"] == 1002:
                banmessage = bannywanny["errorMessage", "No Ban Message Found."]
                bandetails = bannywanny["errorDetails", []]
                banexpirekey = bandetails(next(iter(bandetails.keys())), None)
                banexpirelist = bannywanny.get(banexpirekey(), [])
                banexpiretime = {
                    banexpirelist[0]
                    if len(banexpirelist) > 0
                    else "Infinite"
                }

                return jsonify({
                    "message": banmessage,
                    "expire": banexpiretime,
                })
            else: 
                errormessage = bannywanny.get("errorMessage", "Unknown error")
                return jsonify({"Error": "PlayFab Error", "Message": errormessage}), 403

@app.route('/api/CachePlayFabId', methods=['POST', 'GET'])
def cache_playfab_id():
    data = request.get_json()
    playfabid = data.get('PlayFabId')
    return playfabid, 200

@app.route('/api/TitleData', methods=['POST', 'GET'])
def title_data():
    titledatas = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.auth_headers(),
    )

    if titledatas.status_code == 200:
        return jsonify(titledatas.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
