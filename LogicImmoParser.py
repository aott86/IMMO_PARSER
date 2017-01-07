from Parser import Parser
from HouseModel import HouseModel
from bs4 import BeautifulSoup
import urllib
import re

trim = re.compile(r'\s+')
findNumber = re.compile(r'([0-9]{1,10})')
findAlpha = re.compile('[a-zA-Z -]+')

class LogicImmoParser(Parser):
    def getNextPageUrl(self, housesListPageHtml):
        pagingHTML = housesListPageHtml.find('link', rel='prefetch')
        if (pagingHTML):
            return pagingHTML.get('href')
        else:
            return ''

    def parseHtmlHouseListPage(self,housesListPageHtml):
        print('Parse logic immo house list')
        for summaryHtml in housesListPageHtml.find_all('div',class_='offer-block'):
            # print('------------------------------')
            moreDetailLink = summaryHtml.find('a', class_='offer-link').get('href')

            if(moreDetailLink != 'http://www.orpi.com'):
                house = self.parseHouseHtml(moreDetailLink)

                thumbHtml = summaryHtml.find(class_='thumb-link')
                if (thumbHtml):
                    house.imageLink = thumbHtml.find('img').attrs.get('src')

                self.createOrUpdateHouse(house)

    def parseHouseHtml(self, houseLink):
        house = HouseModel()
        house.source = 'logicimmo'
        house.link = houseLink
        house.isPro = True
        oneHouseHtml = BeautifulSoup(urllib.request.urlopen(houseLink), "html.parser")

        idHtml = oneHouseHtml.find(id='offer_navigation')
        if idHtml:
            house.id = "logicimmo_"+idHtml.attrs.get('data-offer-id')

        itemImageHtml = oneHouseHtml.find(class_='picto-img')
        if itemImageHtml:
            house.hasPictures = (int(itemImageHtml.get_text()) >0)

        titleHtml = oneHouseHtml.find('h1')
        if titleHtml:
            house.title = titleHtml.get_text().strip()

        typeHtml = oneHouseHtml.find(class_='offer-type')
        if typeHtml:
            house.type = typeHtml.find('p').get_text().strip().lower()

        superficieHtml = oneHouseHtml.find(class_='offer-area-number')
        if superficieHtml:
            house.surface = int(superficieHtml.get_text())

        priceHtml = oneHouseHtml.find(class_='main-price')
        if priceHtml:
            house.price = int(findNumber.findall(trim.sub('',priceHtml.get_text()))[0])

        cityHtml = oneHouseHtml.find(class_='offer-locality')
        if cityHtml:
            cityWithoutNorm = findAlpha.findall(cityHtml.find('p').get_text())[0].strip()
            house.city=self.normalizeCity(cityWithoutNorm)
            house.postalCode = int(findNumber.findall(cityHtml.find('p').get_text())[0])

        descriptionHtml = oneHouseHtml.find(class_='offer-description-text')
        if descriptionHtml:
            house.description = descriptionHtml.find('meta').attrs.get('content')

        nbRoomsHtml = oneHouseHtml.find(class_='offer-rooms-number')
        if nbRoomsHtml:
            house.nbrRooms = int(nbRoomsHtml.get_text().strip())

        gesHtml = oneHouseHtml.find(class_='greenhouse-summary')
        if gesHtml:
            house.ges =gesHtml.get_text().strip()[0]

        cesHtml = oneHouseHtml.find(class_='energy-summary')
        if cesHtml:
            house.ces = cesHtml.get_text().strip()[0]

        return house