import urllib.parse
import time
from selenium import webdriver
from selenium.common import exceptions
from bs4 import BeautifulSoup
import json
from selenium.webdriver.chrome.options import Options

SLEEPTIME = 2
PAGETIME = .5

def getCitations(paperID, myDict):
    browser = configureBrowser()
    query = "https://academic.microsoft.com/paper/" + paperID
    browser.get(query)
    time.sleep(SLEEPTIME)
    myHTML = BeautifulSoup(browser.page_source, features="html.parser")

    try:
        while True:
            papersList = myHTML.find_all("ma-card", attrs={"au-target-id":"418"})

            for papers in papersList:
                currPaper = papers.find_all("a", attrs={"au-target-id":"492"})
                paperID = currPaper[0]["data-appinsights-paper-id"]
                currNum = myDict.get(paperID, 0)
                myDict[paperID] = currNum + 1

            link = browser.find_element_by_xpath("//i[@au-target-id='382']")
            link.click()
            print("found it, sleeping now.")
            myHTML = BeautifulSoup(browser.page_source, features="html.parser")
            time.sleep(PAGETIME)

    except exceptions.NoSuchElementException:
        pass
    except exceptions.ElementClickInterceptedException:
        pass
    except:
        pass
    browser.quit()


def findInitialPaper(paperName):
    query = "https://academic.microsoft.com/search?q=" + urllib.parse.quote(paperName)
    browser = configureBrowser()
    browser.get(query)
    time.sleep(SLEEPTIME)
    myHTML = BeautifulSoup(browser.page_source, features="html.parser")

    mainPaper = myHTML.find_all("ma-card")[0]
    mainPaperID = mainPaper.find_all("a", attrs={"au-target-id":"398"})[0]["data-appinsights-paper-id"]
    browser.quit()
    return mainPaperID


def configureBrowser():
    chrome_options = Options()
    chrome_options.add_argument("disable-extensions")
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1200x600')
    return webdriver.Chrome(options=chrome_options)


def lookUpPaper(paperID):
    query = "https://academic.microsoft.com/paper/" + paperID
    browser = configureBrowser()
    browser.get(query)
    time.sleep(SLEEPTIME)
    myHTML = BeautifulSoup(browser.page_source, features="html.parser")
    paperYear = myHTML.find_all("span", attrs={"class":"year"})[0].string
    paperLink = myHTML.find_all("a", attrs={"au-target-id":"19"})[0]["href"]
    paperName = myHTML.find_all("div", attrs={"au-target-id":"72"})[0]["data-appinsights-query"]

    returnVals = (str(paperName),int(paperYear),str(paperLink))
    browser.quit()
    return returnVals
    


def getGenerations(paperName, numGens):
    bigPaperList = {}
    alreadySearched = []
    # start the dictionary with the main paper
    myID = findInitialPaper(paperName)
    bigPaperList[myID] = 1

    for x in range(numGens):
        for paper in list(bigPaperList):
            if paper not in alreadySearched:
                alreadySearched.append(paper)
                getCitations(paper,bigPaperList)
    return bigPaperList


def loadPaperList(fileName):
    with open(fileName) as json_file: 
        return json.loads(json_file.read())

def savePaperList(fileName, myDict):
    with open(fileName, "w") as json_file: 
        json_file.write(json.dumps(myDict))


def printTopN(myDict, topN, fileName):
    if len(myDict) < topN:
        topN = len(myDict)
    sortedPapers = sorted(myPaperDict.items(), key=lambda x: x[1], reverse=True)
    topPapers = []

    with open(fileName, "w") as myFile:
        for x in range(topN):
            paper = lookUpPaper(str(sortedPapers[x][0]))
            paperTimes = sortedPapers[x][1]
            myFile.write("Paper {}: Appeared {} times.\n".format(x+1, paperTimes))
            for stat in paper:
                myFile.write(str(stat))
                myFile.write("\n")
            myFile.write("\n\n\n")


paperName = "A Survey of General-Purpose Computation on Graphics Hardware"
paperName = "FlashGraph: processing billion-node graphs on an array of commodity SSDs"
paperName = "Grandmaster level in StarCraft II using multi-agent reinforcement learning"

myFileName = "paperList.json"
myPaperDict = getGenerations(paperName, 3)
savePaperList(myFileName, myPaperDict)
printTopN(myPaperDict,15,"topN.txt")
