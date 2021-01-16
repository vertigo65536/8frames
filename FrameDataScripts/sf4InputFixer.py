import os, json

chars = os.listdir()

for i in range(len(chars)):
    if not chars[i].endswith(".json"):
        continue
    with open(chars[i]) as json_file:
        print("Processing " + chars[i])
        moveList = json.load(json_file)
        for key, value in moveList['moves'].items():
            if 'chargeDirection' in value:
                value['input'] = value['chargeDirection'] + value['input']
                del value['chargeDirection']
            moveList['moves'][key] = value
    with open(chars[i], 'w') as json_file:
        json.dump(moveList, json_file, indent=4)
