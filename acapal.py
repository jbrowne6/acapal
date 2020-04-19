import urllib.parse
import time
from selenium import webdriver
from selenium.common import exceptions
from bs4 import BeautifulSoup
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SLEEPTIME = 3 # timeout for mainpage loads
SHORTTIME = 1 # rest time between papers
PAGETIME = .75 # timeout for within page loads

def getCitations(paperID, myDict):
    browser = configureBrowser()
    query = "https://academic.microsoft.com/paper/" + paperID
    browser.get(query)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//ma-card[@au-target-id='418']"))
        WebDriverWait(browser, SLEEPTIME).until(element_present)
    except exceptions.TimeoutException:
        print ("Timed out waiting to find a Paper.")
        browser.quit()
        return None
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
            # Next two lines ensure tags are available before proceeding.  Will cause timeout error otherwise.
            element_present = EC.presence_of_element_located((By.XPATH, "//ma-card[@au-target-id='418']"))
            WebDriverWait(browser, PAGETIME).until(element_present)
            myHTML = BeautifulSoup(browser.page_source, features="html.parser")

    except exceptions.NoSuchElementException:
        print ("This paper didn't have the right tags.")
        pass
    except exceptions.ElementClickInterceptedException:
        print ("The chrome browser lost focus.")
        pass
    except exceptions.TimeoutException:
        print ("Timed out looking for citations.")
        pass
    except:
        print ("Something went wrong.  Not sure what.")
        pass
    browser.quit()


def findInitialPaper(paperName):
    query = "https://academic.microsoft.com/search?q=" + urllib.parse.quote(paperName)
    browser = configureBrowser()
    browser.get(query)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//a[@au-target-id='398']"))
        WebDriverWait(browser, SLEEPTIME).until(element_present)
    except exceptions.TimeoutException:
        print ("Timed out waiting to find initial Paper.")
        exit()

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
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//div[@au-target-id='72']"))
        WebDriverWait(browser, SLEEPTIME).until(element_present)
    except exceptions.TimeoutException:
        print ("Timed out waiting to find initial Paper.")
        exit()
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
                print("Taking a short break between papers.")
                time.sleep(SHORTTIME)
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

    print("Printing top {} to file.".format(topN))
    with open(fileName, "w") as myFile:
        for x in range(topN):
            paper = lookUpPaper(str(sortedPapers[x][0]))
            print("Printing paper {} details.".format(x))
            time.sleep(SHORTTIME)
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
myPaperDict = getGenerations(paperName, 2)
savePaperList(myFileName, myPaperDict)
printTopN(myPaperDict,15,"topN.txt")
