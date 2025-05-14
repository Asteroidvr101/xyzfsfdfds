import datetime
from flask import Flask, request, jsonify
import requests
from werkzeug.datastructures import headers
from datetime import datetime, timedelta

class GameSettings:
    def __init__(self):
        self.TitleId: str = "7AF94"
        self.SecretKey: str = "GBIPB74594RF9UDYHIAKASEJ1WG66KWWF4FAPKJK1WYZCC94S7"
        self.ApiKey: str = "OC|9951834934884203|b1e4d8e8c01190aacc38da98c8e1234e"

    def auth_headers(self):
        return {
            "Content-Type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = GameSettings()
app = Flask(__name__)

@app.route('/')
def index():
    return 'I Think The Backend Is Working'

@app.route('/api/PlayFabAuthentication', methods=['POST', 'GET'])
def playfab_auth():
    if 'UnityPlayer' not in request.headers['User-Agent']:
        return jsonify({
            "BanMessage": "Um What The Fuck",
            "BanExpirationTime": "Infinite"
        }), 403

    data = request.get_json()
    oculusid = data.get("OculusId")
    AppId = data.get("AppId")
    CustomId = data.get("CustomId")
    nonce = data.get("nonce")

    oculus_response = requests.post("https://graph.oculus.com/user_nonce_validate", json={
        "access_token": f"{settings.ApiKey}",
        "nonce": nonce,
        "user_id": oculusid
    })
    print(oculus_response.status_code)
    print(oculus_response)
    if oculus_response.status_code != 200 or not oculus_response.json().get("is_valid", False):
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403
    
    blockedcustoms = ["OCULUS0", "PI", "DLL", "HACKER"]

    if blockedcustoms in CustomId:
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    if not CustomId.startsWith("OCULUS"):
        return jsonify({
            "BanMessage": "Your account has been traced and you have been banned.",
            "BanExpirationTime": "Indefinite"
        }), 403

    if AppId != settings.TitleId:
        return jsonify({
            "BanMessage": "Why Does The App Id Not Match Huh",
            "BanExpirationTime": "Indefinite"
        }), 403
            
    requestlog = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomID",
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
    return 'PlayFabId I Think Um Whatever', 200

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

@app.route("/api/CheckForBadName", methods=["POST", "GET"])
def check_for_bad_name():
        rjson = request.get_json() 
        function_result = rjson["FunctionArgument"]
        playfab_id = rjson["CallerEntityProfile"]["Lineage"]["MasterPlayerAccountId"]
        name = function_result["name"].upper()
        forRoom = function_result["forRoom"]

        if forRoom == True:
            return jsonify({"result": 0})

        link_response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Admin/UpdateUserTitleDisplayName",
            json={
                "DisplayName": name,
                "PlayFabId": playfab_id,
            },
            headers=settings.auth_headers(),
        ).json()
        return jsonify({"result": 0})


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


@app.route("/api/photon", methods=["POST"])
def photonauth():
        print(f"Received {request.method} request at /api/photon")
        getjson = request.get_json()
        Ticket = getjson.get("Ticket")
        Nonce = getjson.get("Nonce")
        Platform = getjson.get("Platform")
        UserId = getjson.get("UserId")
        nickName = getjson.get("username")
        if request.method.upper() == "GET":
            rjson = request.get_json()
            print(f"{request.method} : {rjson}")

            userId = Ticket.split('-')[0] if Ticket else None
            print(f"Extracted userId: {UserId}")

            if userId is None or len(userId) != 16:
                print("Invalid userId")
                return jsonify({
                    'resultCode': 2,
                    'message': 'Invalid token',
                    'userId': None,
                    'nickname': None
                })

            if Platform != 'Quest':
                return jsonify({'Error': 'Bad request', 'Message': 'Invalid platform!'}),403

            if Nonce is None:
                return jsonify({'Error': 'Bad request', 'Message': 'Not Authenticated!'}),304

            req = requests.post(
                url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
                json={"PlayFabId": userId},
                headers={
                    "content-type": "application/json",
                    "X-SecretKey": settings.SecretKey
                })

            print(f"Request to PlayFab returned status code: {req.status_code}")

            if req.status_code == 200:
                nickName = req.json().get("UserInfo",
                                          {}).get("UserAccountInfo",
                                                  {}).get("Username")
                if not nickName:
                    nickName = None

                print(
                    f"Authenticated user {userId.lower()} with nickname: {nickName}"
                )

                return jsonify({
                    'resultCode': 1,
                    'message':
                    f'Authenticated user {userId.lower()} title {settings.TitleId.lower()}',
                    'userId': f'{userId.upper()}',
                    'nickname': nickName
                })
            else:
                print("Failed to get user account info from PlayFab")
                return jsonify({
                    'resultCode': 0,
                    'message': "Something went wrong",
                    'userId': None,
                    'nickname': None
                })

        elif request.method.upper() == "POST":
            rjson = request.get_json()
            print(f"{request.method} : {rjson}")

            ticket = rjson.get("Ticket")
            userId = ticket.split('-')[0] if ticket else None
            print(f"Extracted userId: {userId}")

            if userId is None or len(userId) != 16:
                print("Invalid userId")
                return jsonify({
                    'resultCode': 2,
                    'message': 'Invalid token',
                    'userId': None,
                    'nickname': None
                })

            req = requests.post(
                 url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
                 json={"PlayFabId": userId},
                 headers={
                     "content-type": "application/json",
                     "X-SecretKey": settings.SecretKey
                 })

            print(f"Authenticated user {userId.lower()}")
            print(f"Request to PlayFab returned status code: {req.status_code}")

            if req.status_code == 200:
                 nickName = req.json().get("UserInfo",
                                           {}).get("UserAccountInfo",
                                                   {}).get("Username")
                 if not nickName:
                     nickName = None
                 return jsonify({
                     'resultCode': 1,
                     'message':
                     f'Authenticated user {userId.lower()} title {settings.TitleId.lower()}',
                     'userId': f'{userId.upper()}',
                     'nickname': nickName
                 })
            else:
                 print("Failed to get user account info from PlayFab")
                 successJson = {
                     'resultCode': 0,
                     'message': "Something went wrong",
                     'userId': None,
                     'nickname': None
                 }
                 authPostData = {}
                 for key, value in authPostData.items():
                     successJson[key] = value
                 print(f"Returning successJson: {successJson}")
                 return jsonify(successJson)
        else:
             print(f"Invalid method: {request.method.upper()}")
             return jsonify({
                 "Message":
                 "Use a POST or GET Method instead of " + request.method.upper()
             })


def ReturnFunctionJson(data, funcname, funcparam={}):
        print(f"Calling function: {funcname} with parameters: {funcparam}")
        rjson = data.get("FunctionParameter", {})
        userId = rjson.get("CallerEntityProfile",
                           {}).get("Lineage", {}).get("TitlePlayerAccountId")

        print(f"UserId: {userId}")

        req = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
            json={
                "PlayFabId": userId,
                "FunctionName": funcname,
                "FunctionParameter": funcparam
            },
            headers={
                "content-type": "application/json",
                "X-SecretKey": settings.SecretKey
            })

        if req.status_code == 200:
            result = req.json().get("data", {}).get("FunctionResult", {})
            print(f"Function result: {result}")
            return jsonify(result), req.status_code
        else:
            print(f"Function execution failed, status code: {req.status_code}")
            return jsonify({}), req.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
