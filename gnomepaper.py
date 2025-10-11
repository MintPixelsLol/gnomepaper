import os, sys, subprocess, time, shutil
#checks before initializing
print("Checking compatibility...")
canRun = True
canRoot = os.geteuid() == 0
errorReason = "none"
if sys.platform == "linux" or sys.platform == "linux2":
    if os.path.isdir("/usr/share/backgrounds/gnome") and os.path.isdir("/usr/share/gnome-background-properties"):
        de = subprocess.run("echo $XDG_CURRENT_DESKTOP", shell=True, capture_output=True).stdout
        if not "GNOME" in str(de):
            print("current de INVALID")
            canRun = False
            errorReason = f"GNOME not running, this does NOT work for other DEs. Current DE: {str(de)}"
    else:
        print("path INVALID")
        canRun = False
        errorReason = "Can't find the wallpaper paths - is GNOME even installed??"
else:
    print("os INVALID")
    canRun = False
    errorReason = f"Expected platform to be 'linux', or 'linux2', got '{sys.platform}' instead."
if not canRun:
    sys.exit(f"Couldn't launch: {errorReason}")
else:
    print(f"Success!")
canRoot = os.geteuid() == 0
if canRoot:
    uid = int(os.environ["SUDO_UID"])
    gid = int(os.environ["SUDO_GID"])
#checks over
import xml.etree.ElementTree as ET
from datetime import datetime
run = True
list = {}
validFile = False
if canRun:
    print("gnomepaper\nversion: 1.0 - one and (hopefully) only\nThis tool is NOT designed to be idiot-proof, but it has some failsaves for the *most common* user errors.")
    if canRoot:
        print("\nCommands:\nList wallpapers\nAdd wallpaper\nRemove wallpaper\nBackup wallpapers\neXit program")
    else:
        print("\nCommands:\nList wallpapers\nBackup wallpapers\neXit program\n\nSome sommands are NOT available, to fix this, run this script using sudo.\n")
    while run:
        if canRoot:
            o = input("(Larbx) >>> ")
        else:
            o = input("(Lbx) >>> ")
        o = o.lower()
        if o.startswith("l") or o.strip() == "":
            print("Properly registered wallpaper options:")
            list = []
            i = 0
            for filename in os.listdir("/usr/share/gnome-background-properties"):
                if not filename.endswith('.xml'): continue
                try:
                    file = ET.parse(os.path.join("/usr/share/gnome-background-properties", filename))
                    root = file.getroot()
                    wallName = root.find("wallpaper").find("name").text
                    wallPath = root.find("wallpaper").find("filename").text
                    if wallPath and wallName:
                        list.append(f"{i} | {wallName} | {filename}")
                        i += 1
                except ET.ParseError:
                    pass
            for i in list: print(i)
        if o.startswith("a") and canRoot:
            useDark = True
            wName = input("Enter the wallpaper's name >>> ")
            fileName = "gwot_"+wName.strip().lower().replace(" ", "-")+".xml"
            if os.path.isfile(os.path.join("/usr/share/gnome-background-properties", fileName)):
                print(f"File name already used, choose a different one. ({fileName})")
                continue
            wPath = input("Enter a path to the light mode variant of the wallpaper >>> ")
            wPath = wPath.strip()
            if wPath.startswith("'") and wPath.endswith("'"):
                wPath = wPath[1:-1]
            if not os.path.isfile(wPath):
                print(f"'{wPath}' is not a file.")
                continue
            wPath2 = input("Enter a path to the dark mode variant of the wallpaper (optional) >>> ")
            wPath2 = wPath2.strip()
            if wPath2.startswith("'") and wPath2.endswith("'"):
                wPath2 = wPath2[1:-1]
            if not os.path.isfile(wPath2):
                print("Skipping dark wallpaper...")
                useDark = False
            print(f"File name : {fileName}\n|- Name: {wName}\n|- Image path: {wPath}")
            if useDark: print(f"|- Image path (dark): {wPath2}")
            if input("Create a wallpaper? (Yn) >>> ").lower().strip().startswith("n"):
                continue
            print("Copying images...")
            finalWPath = shutil.copy(wPath, "/usr/share/backgrounds/gnome")
            if useDark: finalWPath2 = shutil.copy(wPath2, "/usr/share/backgrounds/gnome")
            print("Creating the XML file...")
            root = ET.Element("wallpapers")
            childA = ET.SubElement(root, "wallpaper")
            childA.set("deleted", "false")
            nameChild = ET.SubElement(childA, "name")
            nameChild.text = wName
            pathAChild = ET.SubElement(childA, "filename")
            pathAChild.text = finalWPath
            if useDark:
                pathBChild = ET.SubElement(childA, "filename-dark")
                pathBChild.text = finalWPath2
            optionsChild = ET.SubElement(childA, "options")
            optionsChild.text = "zoom"
            wallTree = ET.ElementTree(root)
            wallTree.write(os.path.join("/usr/share/gnome-background-properties", fileName))
            print("Done!")
            
        if o.startswith("r") and canRoot:
            t = input("Enter the wallpaper's xml file name to remove it (example.xml) >>> ")
            if os.path.isfile(os.path.join("/usr/share/gnome-background-properties", t)):
                try:
                    file = ET.parse(os.path.join("/usr/share/gnome-background-properties", t))
                    root = file.getroot()
                    wallName = root.find("wallpaper").find("name").text
                    wallPath = root.find("wallpaper").find("filename").text
                    try:
                        wallPath2 = root.find("wallpaper").find("filename-dark").text
                    except:
                        wallPath2 = False
                    if wallName and wallPath:
                        print(f"Name: {wallName}")
                        print("Files to delete:")
                        print(f"{os.path.join("/usr/share/gnome-background-properties", t)}\n|- {wallPath}")
                        if wallPath2:
                            print(f"|- {wallPath2}")
                        if input("You cannot undo this action, continue? (yN) >>> ").lower() == "y":
                            os.remove(os.path.join("/usr/share/gnome-background-properties", t))
                            os.remove(wallPath)
                            if wallPath2: os.remove(wallPath2)
                            if os.path.isfile(os.path.join("/usr/share/gnome-background-properties", t)) or os.path.isfile(wallPath):
                                print("FAILED to remove the wallpaper. I'm sorry.")
                            else:
                                print("Successfully removed the wallpaper.")
                        else:
                            print("Cancelled.")
                except: print("Something went wrong, maybe file structure is invalid?")
            else:
                print("Invalid file name, you can find them by listing wallpapers.")
        if o.startswith("b"):
            if not os.path.isdir("backups"): 
                os.mkdir("backups")
                if canRoot:
                    os.chown("backups", uid, gid)
            cTime = datetime.now()
            dName = f"backups/{cTime.year}-{cTime.month}-{cTime.day}/{cTime.hour}:{cTime.minute}:{cTime.second}.{cTime.microsecond}"
            dName2 = f"backups/{cTime.year}-{cTime.month}-{cTime.day}"
            os.makedirs(dName)
            shutil.copytree("/usr/share/gnome-background-properties", f"{dName}/gnome-background-properties")
            shutil.copytree("/usr/share/backgrounds/gnome", f"{dName}/gnome")
            if os.path.isdir(f"{dName}/gnome") and os.path.isdir(f"{dName}/gnome-background-properties"):
                if canRoot:
                    os.chown(dName2, uid, gid)
                    os.chown(dName, uid, gid)
                    os.chown(f"{dName}/gnome", uid, gid)
                    os.chown(f"{dName}/gnome-background-properties", uid, gid)
                print("Success!")
            else:
                print("FAILED to backup the wallpapers. I'm sorry.")
        if o.startswith("x"): run = False
