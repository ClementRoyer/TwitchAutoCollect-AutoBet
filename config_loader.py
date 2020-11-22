from configparser import SafeConfigParser

def load(path):
    parser = SafeConfigParser()
    parser.read(path)

    obj = {
        "debug": False,
        "stream": "",
        "token": "" 
    }

    obj["debug"] = parser.getboolean("my-config", "debug")
    obj["stream"] = parser.get("my-config", "stream")
    obj["token"] = parser.get("my-config", "token")
    obj["chrome_path"] = parser.get("my-config", "chrome_path")

    return obj