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
            moreDetailLink = "http://www.explorimmo.com" + summaryHtml.attrs.get('href')
            house = self.parseHouseHtml(moreDetailLink)

            thumbHtml = summaryHtml.find('img')
            if (thumbHtml):
                house.imageLink = thumbHtml.attrs.get('src')

            self.createOrUpdateHouse(house);

    def extractid(self,href):
        myid = re.search("\d+", href).group(0)
        return "explorimmo_"+str(myid)

    def parseHouseHtml(self, houseLink):
        house = HouseModel()
        house.source = 'explorimmo'
        house.link = houseLink
        house.id = self.extractid(houseLink)
        house.isPro = True
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

        cityHtml = oneHouseHtml.find(class_='informations-localisation')
        if cityHtml:
            cityWithoutNorm = cityHtml.find(text=True).strip()
            house.city=self.normalizeCity(cityWithoutNorm)

        descriptionHtml = oneHouseHtml.find(class_='description')
        if descriptionHtml:
            house.description = descriptionHtml.get_text().strip()

        featuresHtml = oneHouseHtml.find(class_='features')

        for featureHtml in featuresHtml.find_all('li'):
            featureName = featureHtml.find(class_='name').get_text().strip()
            if featureName == 'Surface':
                surfaceText=featureHtml.find(class_='value').get_text().strip()
                if surfaceText != 'NC':
                    house.surface = int(findNumber.findall(surfaceText)[0])
                else:
                    house.surface =1

            elif featureName == 'Nombre de pièces':
                nbPieceText = featureHtml.find(class_='value').get_text().strip()
                if nbPieceText != 'Non précisé':
                    house.nbrRooms = int(nbPieceText)


        nrjHTML = oneHouseHtml.find(class_='energy-consumption')
        house.ces = nrjHTML.find_all('li')[0].find('span').get_text().strip()[0]
        house.ges = nrjHTML.find_all('li')[1].find('span').get_text().strip()[0]
        return house