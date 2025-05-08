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
    return 'I Think The Backend Is Working'

@app.route('/api/PlayFabAuthentication', methods=['GET', 'POST'])
def playfab_authentication():
    
    skibidi = request.get_json()
    oculusid = skibidi.get('OculusId')
    customid = skibidi.get('CustomId')

    if customid.startswith("OCULUS"):
        return jsonify({
            "BanMessage": "Invalid Custom Id",
            "BanExpirationTime": "INFINITE"
        }), 403

    if 'UnityPlayer' not in request.headers.get('User-Agent', ''):
        return jsonify({
            "BanMessage": "Modding The Game???",
            "BanExpirationTime": "Indefinite"
        }), 403

    
    loginreq = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
        headers=settings.get_auth_headers(),
        json={
            "CreateAccount": True,
            "CustomId": "OCULUS" + oculusid
        }
    )

    if loginreq.status_code == 200:
        rjson = loginreq.json()
        return jsonify({
            "PlayFabId": rjson["data"]["PlayFabId"],  
            "SessionTicket": rjson["data"]["SessionTicket"],  
            "EntityToken": rjson["data"]["EntityToken"]["EntityToken"],  
            "EntityId": rjson["data"]["EntityToken"]["Entity"]["Id"], 
            "EntityType": rjson["data"]["EntityToken"]["Entity"]["Type"]
        })
    else:
        banshit = loginreq.json()
        if banshit.get("errorCode") == 1002:
            banmessage = banshit.get("errorMessage")
            bandetails = banshit.get("errorDetails", "message")
            banexpirekey = bandetails(next(iter(bandetails.keys())), None)
            banexpirelist = banshit.get(banexpirekey(), [])
            banexpiretime = banexpirelist[0] if len(banexpirelist) else "Infinite"
            return jsonify({
                "BanMessage": banmessage,
                "BanExpirationTime": banexpiretime
            }), 403


@app.route('/api/TitleData', methods=['GET', 'POST'])
def title_data():
    title_data_req = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.get_auth_headers(),
    )

    if title_data_req.status_code == 200:
        return jsonify(title_data_req.json())

@app.route('/api/CachePlayFabId', methods=['POST', 'GET'])
def cache_playfab_id():
    return "HAHA", 200



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
