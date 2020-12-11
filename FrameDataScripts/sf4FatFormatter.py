import json, os, shutil

def getPath(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

with open('usf4Data.json') as json_file:
    data = json.load(json_file)

folder = getPath("sf4")
if os.path.isdir(folder):
    shutil.rmtree(folder)
os.mkdir(folder)

for charName, character in data.items():
    print("Formatting " + charName)
    for key, move in character['moves'].items():
        #print(move)
        moveInput = ""
        if 'moveMotion' in move:
            moveInput = move['moveMotion'] + "+"
        if 'moveButton' in move:
            moveInput = moveInput + move['moveButton']
        moveInput = moveInput.replace("none", "").strip("+").strip()
        if moveInput == "":
            moveInput = "None"
        if ">" in key:
            print(key)
        else:
            character['moves'][key]['input'] = moveInput
    with open(os.path.join(folder, charName + ".json"), 'w') as outfile:
        json.dump(character, outfile, indent=4)
