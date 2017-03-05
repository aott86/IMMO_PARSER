# anchor extraction from html document
from bs4 import BeautifulSoup
import urllib.request
import sys

from ExplorimmoParser import ExplorimmoParser
from HouseDao import HouseDao
from LBCParser import LBCParser
from LogicImmoParser import LogicImmoParser
from SeLogerParser import SeLogerParser

if  len(sys.argv) != 4:
    print ('Wrong number of arguments', len(sys.argv))
    print ('usage: HouseExtractor.py  <path to wkhtmltopdf> <mongodb-url> <path to url file>')
    sys.exit(-1)

def chooseParser(url):
    if 'www.leboncoin.fr' in url:
        return LBCParser()
    elif 'www.logic-immo.com' in url:
        return LogicImmoParser()
    elif 'www.explorimmo.com' in url:
        return ExplorimmoParser()
    elif 'www.seloger.com' in url:
        return SeLogerParser()
    else:
        print('ERROR: no parser exists for the url '+ url)
        sys.exit(-1)

def load_url(url):
    pageNum = 1
    pagelimit = 100
    pageToAnalyzeUrl = url

    parser = chooseParser(url)
    while((not pageToAnalyzeUrl == '') & (not pageNum == pagelimit)):
        print('pageNum:' + str(pageNum))
        print('pageToAnalyzeUrl:' + pageToAnalyzeUrl)
        webpage = urllib.request.urlopen(pageToAnalyzeUrl)
        housesListPageHtml = BeautifulSoup(webpage, "html.parser")
        parser.parseHtmlHouseListPage(housesListPageHtml);
        pageToAnalyzeUrl = parser.getNextPageUrl(housesListPageHtml)
        pageNum +=1

# MAIN
for f in open(sys.argv[3]):
    urls = f.split("\r")
    for url in urls:
        load_url(url)

houseDao = HouseDao()
houseCheckDeletion = houseDao.getUndeletedHouses()
print('Nb house not deleted: ' + str(houseCheckDeletion.count()))
for house in houseCheckDeletion:
    try:
        urllib.request.urlopen(house['link'])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print ('House is deleted: '+house['_id'])
            houseDao.updateHouseDeleted(house['_id'])