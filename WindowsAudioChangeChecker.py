import copy
import os
def makeRegistryDict(path):
    reg_dict = {}
    last_path = ""
    line = ""
    with open(path, 'r', encoding='utf16') as file:
        for raw_line in file:
            current_line = raw_line.rstrip("\r\n")
            # we got an emtpy line, so it is a new block
            if len(line) == 1:
                last_path = ""
                line = ""

            # we detect if line's not supposed to be over
            elif current_line.endswith("\\"):
                line += current_line.strip("\\").lstrip()

            else:
                #the last line was a multi-line
                if len(line)>0:
                    line += current_line.strip("\\").lstrip()

                #last line was not a multi-line
                else:
                    line = current_line

                #empty line
                if len(line)==0:
                    last_path = ""

                # we got a path
                elif "[" in line:
                    #stripping the formatting, i want a string i can use
                    last_path = line.rstrip().replace("[","").replace("]","")

                #we got a key-value pair
                elif "=" in line:

                    #we already have this path, add to it.
                    if last_path in reg_dict.keys():
                        reg_dict[last_path].append(line)
                    else:
                        reg_dict[last_path] = [line]
                    #print(len(line))
                    #print("KV Pair: ",line)

                #debug to detect if we had an edge-case we aren't Handling.
                #The registry Editor version is expected
                else:
                    #print(line) #uncomment to see the registry version twice. anything else is unexpected
                    pass
                #no matter what happens, once we are *done* with a line (single or multi), we empty it
                line = ""
    return reg_dict

def compareLists(listA, listB):
    """
    :param listA: First Comparison list
    :param listB: Second Comparison list
    :rtype: list
    :return: a list of 2 lists, unique entries in listA, unique entries in listB
    """
    a_not_b = []
    b_not_a = []
    for entry in listA:
        if entry in listB:
            listB.remove(entry)
        else:
            a_not_b.append(entry)
    if len(listB) > 0:
        b_not_a = listB
    return [a_not_b,b_not_a]

def compareDicts(dictA,dictB):
    errors = []
    # Parsing the dict_keys object to list to do list things
    keysA = list(dictA.keys())
    keysB = list(dictB.keys())
    for key in keysA:
        #print(key)
        if not key in keysB:
            errors.append(["key not found in B",key])
        else:
            listA = dictA[key]
            listB = dictB[key]
            listErrors= compareLists(dictA[key],dictB[key])
            if len(listErrors[0])>0 or len(listErrors[1])>0:
                #print("WE GOT AN ERROR")
                #print(dictA[key])
                #print(dictB[key])
                errors.append([key,listErrors])
            keysB.remove(key)
    if len(keysB)>0:
        errors.append(["keysB leftover",keysB])
    return errors

def updateNameList(path,regPath):
    knownNames = {}
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                guid, name = line.split("=")
                knownNames[guid] = name
    with open(path, 'a') as names:
        last_guid = ""
        line = ""
        with open(regPath, 'r', encoding='utf16') as file:
            for raw_line in file:
                #print(raw_line)
                current_line = raw_line.rstrip("\r\n")
                #print(len(current_line))
                if len(current_line) == 0:
                    last_path = ""#
                elif "{b3f8fa53-0004-438e-9003-51a46e139bfc},6" in current_line:
                    if last_guid not in knownNames.keys():
                        nameKey, deviceName = current_line.split("=")
                        deviceName = deviceName.strip('"')
                        names.write(last_guid+"="+deviceName+"\n")
                elif "[" in current_line:
                    #trying to extract just the device GUID
                    keyPath = current_line.rstrip().replace("[","").replace("]","")
                    if "{" in keyPath and "}" in keyPath:
                        last_guid = keyPath.split("{")[1].split("}")[0]

                line=""

def makeNewRegistryExport(regKey, filePath):
    os.system('reg export '+regKey+' "'+filePath+'"  /y')

def getNamebyGUID(path,guid):
    knownNames = {}
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                this_guid, name = line.split("=")
                knownNames[this_guid] = name.strip("\r\n")
    if guid in knownNames.keys():
        return knownNames[guid]
    else:
        return guid

def replaceGUIDwithName(entry):
    if "{" in entry and "}" in entry:
        potential_guids = entry.split("{")
        potential_guids.pop(0) # we remove the first element
        for potential in potential_guids:
            potential = potential.split("}")[0]
            if(len(potential)==36):
                entry = entry.replace(potential,getNamebyGUID(idList,potential))
    return entry
def checkIgnore(key):
    for ignore in ignoreList:
        if ignore in key:
            return True
    return False

regKey= "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices" # The Registry Key for audio things
regA = "D:\\dokumente\\AudioExport.reg" # The *old* registry save. the "known good" for compare
regB = "D:\\dokumente\\AudioRegistry.reg" # The new registry save. this gets newly created on runtime
idList ="D:\\dokumente\\AudioGUIDLookup.txt"
ignoreList = ["Level:0","Level:1"]  # this things show up after switching to another default-output and back.
# I do not know what they are, they seem unrelated to volume level.

# We make a new registry export, we wanna see those changes
makeNewRegistryExport(regKey,regB)
# Making white space between the export and outputs
print("")

# Creating the dictionaries for old and new registry export
regDictA=makeRegistryDict(regA)
regDictB=makeRegistryDict(regB)
# And Comparing the two registries for difference
errors =  compareDicts(regDictA,regDictB)
error_amount = 0

# and now the fun part: error-hunting
for error in errors:
    device, errorList = error
    guid = device.split("{")[1].split("}")[0].strip("\r\n")
    folder = device.split("{")[1].split("}")[1].strip("\r\n")
    old, new = errorList
    changed = []
    temp = copy.deepcopy(old)
    # Checking if any are changed
    for suberror in temp:
        key,value=suberror.split("=")
        for sub in new:
            if key in sub:
                old.remove(suberror)
                new.remove(sub)
                # But is it something we don't wanna know?
                if (checkIgnore(key)):
                    continue
                else:
                    changed.append([suberror,sub])
        #print(suberror)
    if len(changed) > 0 or len(old) > 0 or len(new)>0:
        print(getNamebyGUID(idList, guid) + " " + folder + "                     " + guid)
        error_amount += 1
    if len(old)>0:
        print("Missing Entries: ",end='')
        print(old)
    if len(new)>0:
        print("New Entries    : ",end='')
        print(new)
    if len(changed)>0:
        print("Changed Entries: ")
        for change in changed:
            oldChange,newChange = change
            oldChange = replaceGUIDwithName(oldChange)
            newChange = replaceGUIDwithName(newChange)
            print(oldChange)
            print(newChange)
    print("")

if error_amount>0:
    input("Press Enter to Close...")
