import json

def load():
    with open('config.json','r') as f:
        return json.loads(f.read())

