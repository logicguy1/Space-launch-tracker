from bs4 import BeautifulSoup, NavigableString
from colored import fg, attr
import datetime
import requests
import time
import re
import os

r = fg(241) # Setup color variables
r2 = fg(255)
b = fg(31)
w = fg(15)

flush = lambda : os.system('cls' if os.name == 'nt' else 'clear')

def get_launches():
    response = requests.get("https://spaceflightnow.com/launch-schedule/")
    soup = BeautifulSoup(response.text, 'html.parser')

    launchdate = [i.find("span", "launchdate").text for i in soup.find_all("div", "datename")]
    mission = [i.find("span", "mission").text for i in soup.find_all("div", "datename")]
    launchsite = [i.text.split("Launch site: ")[1] for i in soup.find_all("div", "missiondata")]
    launchtime = [i.text.split("Launch site: ")[0].strip().replace("Launch Time: ", "") for i in soup.find_all("div", "missiondata")]
    missionInfo = [i.text.split("[")[0] for i in soup.find_all("div", "missdescrip")]

    return list(zip(mission, launchdate, launchsite, launchtime, missionInfo))

indxTracker = 0
while True:
    if indxTracker % 1000 == 0:
        try:
            launches = get_launches()
            launches2 = launches
        except requests.exceptions.ConnectionError:
            time.sleep(60)
            continue

    size = os.get_terminal_size()
    width = int(size[0] / 3 * 2)
    widLn1 = width - 9
    widLn3 = width - 13

    indx = 0
    println = ""
    for i in launches:
        if indx == 10:
            break

        if "TBD" not in i[1]:
            try:
                checkDate = datetime.datetime.strptime(f"{i[1]}", "%B %d")
                nowDate = datetime.datetime.utcnow()
                res = (checkDate.day + checkDate.month * 30) - (nowDate.day + nowDate.month * 30)
                if res < 0:
                    launches2.remove(i)
                    continue

            except ValueError:
                try:
                    checkDate = datetime.datetime.strptime(f"{i[1]}", "%B")
                    nowDate = datetime.datetime.utcnow()
                    res = (checkDate.day + checkDate.month * 30) - (nowDate.day + nowDate.month * 30)
                    if res < 0:
                        launches2.remove(i)
                        continue
                except ValueError:
                    pass

        widLn2 = width - len(i[1]) - 15
        println += f"""Mission: {i[0]:<{widLn1}}┃┃
Launch Date: {i[1]}  {i[3]:<{widLn2}}┃┃
Launch Site: {i[2]:<{widLn3}}┃┃
{'':<{width}}┃┃
"""
        indx += 1

    println = [x.strip("\n") for x in println.split("\n")]
    println[1] += f"  Next Launch: {launches2[0][0]}"

    temp = re.search(r'\((.*?)\)',launches2[0][3]).group(1).replace(".", "").strip().upper()[:-4]
    launchDate = datetime.datetime.strptime(f"2021 {launches2[0][1]} {temp}", "%Y %B %d %I:%M %p")
    launchDate = datetime.datetime.strptime(f"{launchDate.year}-{'0' if launchDate.month < 10 else ''}{launchDate.month}-{launchDate.day} {launchDate.hour + 4}:{launchDate.minute}:{launchDate.second}", "%Y-%m-%d %H:%M:%S")
    launchDate = launchDate - datetime.datetime.utcnow()
    println[2] += f"  Launch in t-{launchDate.days}d {round(launchDate.seconds / 60 / 60, 2)}h"[:int(width / 2) - 1]
    println[3] += f"  Location: {launches2[0][2]}"

    ascii = f"{launches2[0][4]}\n\n"
    path = os.walk("ships/")
    for root, dirs, files in path:
        for i in files:
            if i[:-4] in launches2[0][0]:
                with open(os.path.join(root, i)) as data:
                    ascii += "\n".join([i.strip("\n") for i in data.readlines()])

    indx = 0
    for x in ascii.split("\n"):
        if x == "":
            indx += 1
        for i in range(0, len(x), int(width / 2) - 4):
            if println[indx + 5].strip() != "":
                try:
                    println[indx + 5] += f"  {x[i:i + int(width / 2) - 4]}"
                    indx += 1
                except IndexError:
                    break
    # println[indx + 5] = f"{println[indx + 5][:-1]}┣{'━' * (int(width / 2) - 1)}"

    flush()

    print("\n".join(println))

    time.sleep(.1)
    indxTracker += 1
