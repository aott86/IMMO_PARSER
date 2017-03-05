#!/usr/bin/env python3.4
from bs4 import BeautifulSoup
import urllib.request
import sys
import logging
import logging.config

from ExplorimmoParser import ExplorimmoParser
from HouseDao import HouseDao
from LBCParser import LBCParser
from LogicImmoParser import LogicImmoParser
from SeLogerParser import SeLogerParser
from datetime import datetime

launchDate= datetime.now();

logging.config.fileConfig(sys.argv[4])

# create logger
logger = logging.getLogger('IMMO_PARSER')

if  len(sys.argv) != 5:
    logger.info ('Wrong number of arguments', len(sys.argv))
    logger.info ('usage: HouseExtractor.py  <path to wkhtmltopdf> <mongodb-url> <path to url file> <path to log file>')
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
        logger.error('ERROR: no parser exists for the url '+url)
        sys.exit(-1)

def load_url(url):
    pageNum = 1
    pagelimit = 100
    pageToAnalyzeUrl = url

    parser = chooseParser(url)
    while((not pageToAnalyzeUrl == '') & (not pageNum == pagelimit)):
        logger.info('pageNum:' + str(pageNum))
        logger.info('pageToAnalyzeUrl:' + pageToAnalyzeUrl)
        webpage = urllib.request.urlopen(pageToAnalyzeUrl)
        housesListPageHtml = BeautifulSoup(webpage, "html.parser")
        parser.parseHtmlHouseListPage(housesListPageHtml);
        pageToAnalyzeUrl = parser.getNextPageUrl(housesListPageHtml)
        pageNum +=1

# MAIN
logger.info('START')
for f in open(sys.argv[3]):
    urls = f.split("\r")
    for url in urls:
        load_url(url)

houseDao = HouseDao()
houseDeleted = houseDao.getDeletedHouses(launchDate)
logger.info('Nb house deleted: ' + str(houseDeleted.count()))
for house in houseDeleted:
    logger.info ('House is deleted: '+house['_id'])
    houseDao.updateHouseDeleted(house['_id'])