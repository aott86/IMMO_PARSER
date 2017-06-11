from Parser import Parser
from HouseModel import HouseModel
from bs4 import BeautifulSoup
import urllib
import re

trim = re.compile(r'\s+')
findNumber = re.compile(r'([0-9]{1,10})')
findAlpha = re.compile('[^\d]+')

class ExplorimmoParser(Parser):
    def getNextPageUrl(self, housesListPageHtml):
        linkHTML = housesListPageHtml.find_all('link')
        for pagingHTML in linkHTML:
            if pagingHTML.attrs.get('rel') == ['next']:
                return urllib.parse.quote(pagingHTML.attrs.get('href'), safe="%/:=&?~#+!$,;'@()*[]")
        else:
            return ''

    def parseHtmlHouseListPage(self,housesListPageHtml):
        for summaryHtml in housesListPageHtml.find_all(class_='js-item-photo'):
            # print('------------------------------')
            if 'explorimmoneuf.com' not in summaryHtml.attrs.get('href'):
                moreDetailLink = "http://www.explorimmo.com" + summaryHtml.attrs.get('href')
                house = self.parseHouseHtml(moreDetailLink)

                thumbHtml = summaryHtml.find('img')
                if (thumbHtml):
                    house.imageLink = thumbHtml.attrs.get('src')

                self.createOrUpdateHouse(house)

    def extractid(self,href):
        myid = re.search("\d+", href).group(0)
        return "explorimmo_"+str(myid)

    def parseHouseHtml(self, houseLink):
        house = HouseModel()
        house.source = 'explorimmo'
        house.link = houseLink
        house.id = self.extractid(houseLink)
        house.isPro = True
        print(houseLink)
        oneHouseHtml = BeautifulSoup(urllib.request.urlopen(houseLink), "html.parser")
        house.hasPictures = True

        titleHtml = oneHouseHtml.find('h1')
        if titleHtml: house.title = titleHtml.find(text=True).strip()

        if re.search('maison', house.title, re.IGNORECASE):
            house.type = 'maison'
        elif re.search('appartement', house.title, re.IGNORECASE):
            house.type = 'appartement'

        priceHtml = oneHouseHtml.find(class_='price')
        if priceHtml:
            house.price = int(findNumber.findall(trim.sub('',priceHtml.get_text()))[0])

        cityHtml = oneHouseHtml.find(class_='city')
        if cityHtml:
            cityWithoutNorm = cityHtml.find(text=True).strip()
            house.city=self.normalizeCity(cityWithoutNorm)

        descriptionHtml = oneHouseHtml.find(class_='description')
        if descriptionHtml:
            house.description = descriptionHtml.get_text().strip()

        house.surface=1
        for featureHtml in oneHouseHtml.find_all('li'):
            featureText = featureHtml.get_text().strip()
            if "m²" in featureText:
                house.surface = int(findNumber.findall(featureText)[0])
            elif "pièces" in featureText:
                house.nbrRooms = int(findNumber.findall(featureText)[0])

        performancesHtml = oneHouseHtml.find(class_='list-performances')
        for performanceHtml in performancesHtml.find_all('li', recursive=False):
            performanceName = performanceHtml.find(class_='name').get_text().strip()
            if performanceName == 'Bilan gaz à effets de serre':
                gesLetter = performanceHtml.find(class_='select-ges').get_text().strip()[10]
                if gesLetter in ['A','B','C','D','E', 'F', 'G']:
                    house.ges = gesLetter
            elif performanceName == 'Bilan énergétique':
                cesLetter = performanceHtml.find(class_='select-energy').get_text().strip()[10]
                if cesLetter in ['A','B','C','D','E', 'F', 'G']:
                    house.ges = cesLetter
                house.ces = cesLetter
        return house