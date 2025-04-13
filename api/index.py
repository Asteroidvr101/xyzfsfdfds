import requests
import random
from flask import Flask, jsonify, request

class GameInfo:

    def __init__(self):
        self.TitleId: str = "24EAA"
        self.SecretKey: str = "DWJJJDDZ36XKTZ7HQA318IY9YQ6AA1ZNZ9XUMAXHA5NPM78ENX"
        self.ApiKey: str = "OC|9571660089556991|5ba1850f236e2977fe89565704afe749"

    def get_auth_headers(self):
        return {
            "content-type": "application/json",
            "X-SecretKey": self.SecretKey
        }


settings = GameInfo()
app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def Rizz():
    return "backend good"

@app.route("/api/CachePlayFabId", methods=["GET", "POST"])
def cacheplayfabid():
  return "", 200

@app.route("/api/PlayFabAuthentication", methods=["GET", "POST"])
def playfab_authentication():
    if 'UnityPlayer' not in request.headers.get('User-Agent', ''):
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403
        
    what_the_BRUH = request.get_json()
    oculus_id = what_the_BRUH.get('OculusId')
    nonce = what_the_BRUH.get("Nonce")

    oculus_response = requests.post("https://graph.oculus.com/user_nonce_validate", json={
        "access_token": f"OC|9571660089556991|5ba1850f236e2977fe89565704afe749",
        "nonce": nonce,
        "user_id": oculus_id
    })
    print(oculus_response.status_code)
    print(oculus_response)
    if oculus_response.status_code != 200 or not oculus_response.json().get("is_valid", False):
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    login_req = requests.post(
        url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId",
        json = {
            "ServerCustomId": "OCULUS" + oculus_id,
            "CreateAccount": True
        },
        headers=settings.get_auth_headers()
    )

    if login_req.status_code == 200:
        rjson = login_req.json()

        session_ticket = rjson.get('data').get('SessionTicket')
        entity_token = rjson.get('data').get('EntityToken').get('EntityToken')
        playfab_id = rjson.get('data').get('PlayFabId')
        entity_id = rjson.get('data').get('EntityToken').get('Entity').get('Id')
        entity_type = rjson.get('data').get('EntityToken').get('Entity').get('Type')

        return jsonify({
            "SessionTicket": session_ticket,
            "EntityToken": entity_token,
            "PlayFabId": playfab_id,
            "EntityId": entity_id,
            "EntityType": entity_type
        }), 200
    else: 
        ban_info = login_req.json()
        if ban_info.get("errorCode") == 1002:
            ban_message = ban_info.get("errorMessage", "No ban message provided.")
            ban_details = ban_info.get("errorDetails", {})
            ban_expiration_key = next(iter(ban_details.keys()), None)
            ban_expiration_list = ban_details.get(ban_expiration_key, [])
            ban_expiration = (
                ban_expiration_list[0]
                if len(ban_expiration_list) > 0
                else "Indefinite"
            )

            return jsonify({
                "BanMessage": ban_expiration_key,
                "BanExpirationTime": ban_expiration,
            }), 403     



@app.route("/api/td", methods=["POST", "GET"])
def titledata():
    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/GetTitleData",
        headers=settings.get_auth_headers())

    if response.status_code == 200:
        return jsonify(response.json().get("data").get("Data"))
    else:
        return jsonify({}), response.status_code

@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
    rjson = request.get_json()

    access_token = rjson.get("userToken")
    user_id = rjson.get("userID")
    nonce = rjson.get("nonce")
    sku = rjson.get("sku")

    response = requests.post(
        url=
        f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={settings.ApiKey}",
        headers={"content-type": "application/json"})

    if response.json().get("success"):
        return jsonify({"result": True})
    else:
        return jsonify({"error": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
