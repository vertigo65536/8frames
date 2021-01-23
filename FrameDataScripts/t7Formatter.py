import os, json

chars = os.listdir()

for i in range(len(chars)):
    if not chars[i].endswith(".json"):
        continue
    with open(chars[i]) as json_file:
        print("Processing " + chars[i])
        charDataList = json.load(json_file)
        moveList = charDataList['movelist']
        moveDict = {}
        for j in range(len(moveList)):
            moveDict[str(j)] = moveList[j]
        charDataList['movelist'] = moveDict
    with open(chars[i], 'w') as json_file:
        json.dump(charDataList, json_file, indent=4)
