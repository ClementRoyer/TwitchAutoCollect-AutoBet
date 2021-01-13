import requests

USER_AGENT  = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

def post_gql_request(token, body):
    r = requests.post("https://gql.twitch.tv/gql",
        json=body,
        headers={"Authorization": "OAuth " + token, "User-Agent": USER_AGENT})
    return r.json()

def getStreamCoins(token, stream):
    body = {"query": "query {user(login: \""+ stream + "\") {channel {self {communityPoints {balance}}}}}"}
    print(body)
    response = post_gql_request(token, body)
    print(response)
    return response["data"]["user"]["channel"]["self"]["communityPoints"]["balance"]

