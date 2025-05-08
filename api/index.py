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

@app.route("/", methods=["POST", "GET"])
def home():
    return jsonify("Life Is Roblox!")


@app.route("/api/PlayFabAuthentication", methods=["GET", "POST"])
def playfab_authentication(): 
    watesigma = request.get_json()
    oculusid = watesigma.get("OculusId")
    request_login = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
        headers=settings.get_auth_headers(),
        json={
            "CreateAccount": True,
            "CustomId": f"OCULUS" + oculusid
        },
    )

    if request_login.status_code == 200:
        jsons = request_login.json()
        return jsonify({
            "SessionTicket": jsons["data"]["SessionTicket"],
            "PlayFabId": jsons["data"]["PlayFabId"],
            "EntityToken": jsons["data"]["EntityToken"]["EntityToken"],
            "EntityId": jsons["data"]["EntityToken"]["Entity"]["Id"],
            "EntityType": jsons["data"]["EntityToken"]["Entity"]["Type"],
        })
    else:
        ban_shit = request_login.json()
        if ban_shit.get("errorCode") == 1002:
            banmessage = ban_shit["errorMessage"]["message"]
            bandetails = ban_shit["errorMessage"][{}]
            banexpirekey = bandetails(next(iter(bandetails.keys())), None)
            banexpirelist = ban_shit.get(banexpirekey(), [])
            banexpiretime = banexpirelist[0]

            return jsonify ({
                    "BanMessage": banmessage,
                    "BanExpirationTime": banexpiretime
                }), 403 

@app.route("/api/TitleData1", methods=["POST", "GET"])
def titledata():

    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.get_auth_headers(),
    )

    if response.status_code == 200:
        return jsonify(response.json().get("data").get("Data"))


@app.route("/api/CachePlayFabId", methods=["POST", "GET"])
def cache_playfab_id():
    return "What The Helly", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
