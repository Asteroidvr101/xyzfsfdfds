import requests
import datetime
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
    elif loginreq.status_code == 403:
            ban_info = loginreq.json()
            if ban_info.get("errorCode") == 1002:
                ban_message = ban_info.get("errorMessage", "No ban message provided.")
                ban_details = ban_info.get("errorDetails", {})
                ban_expiration_key = next(iter(ban_details.keys()), None)
                ban_expiration_list = ban_details.get(ban_expiration_key, [])
                ban_expiration = (
                    ban_expiration_list[0]
                    if len(ban_expiration_list) > 0
                    else "No expiration date provided."
                )
                print(ban_info)
                return (
                    jsonify(
                        {
                            "BanMessage": ban_expiration_key,
                            "BanExpirationTime": ban_expiration,
                        }
                    ),
                    403,
                )
            else:
                error_message = ban_info.get(
                    "errorMessage", "Forbidden without ban information."
                )
                return (
                    jsonify({"Error": "PlayFab Error", "Message": error_message}),
                    403,
                )
        else:
            error_info = loginreq.json()
            error_message = error_info.get("errorMessage", "An error occurred.")
            return (
                jsonify({"Error": "PlayFab Error", "Message": error_message}),
                loginreq.status_code,
            )




@app.route('/api/TitleData', methods=['GET', 'POST'])
def title_data():
    if request.method != 'POST':
        today = datetime.datetime.now()
        startweek = today - datetime.timedelta(days=today.weekday())
        endweek = startweek + datetime.timedelta(days=6)
        itemname1 = {
            "LBACP."
        }

        itemname2 = {
            "LBAAK."
        }

        itemname3 = {
            "LBAAD."
        }

        data = {
            "TOTD": [{
                "PedestalID": "CosmeticStand1",
                "ItemName": itemname1,
                "StartTimeUTC": startweek.strftime("%Y-%m-%d"),
                "EndTimeUTC": endweek.strftime("%Y-%m-%d")
            },
            {
                "PedestalID": "CosmeticStand2",
                "ItemName": itemname2,
                "StartTimeUTC": startweek.strftime("%Y-%m-%d"),
                "EndTimeUTC": endweek.strftime("%Y-%m-%d")
            },
            {
                "PedestalID": "CosmeticStand3",
                "ItemName": itemname3,
                "StartTimeUTC": startweek.strftime("%Y-%m-%d"),
                "EndTimeUTC": endweek.strftime("%Y-%m-%d")
            }]
        }

        return jsonify(data)

        
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
