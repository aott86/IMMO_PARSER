from Parser import Parser
from HouseModel import HouseModel
from bs4 import BeautifulSoup
import urllib
import re

trim = re.compile(r'\s+')
findNumber = re.compile(r'([0-9]{1,10})')
findAlpha = re.compile('[^\d]+')

class LBCParser(Parser):
    def getNextPageUrl(self, housesListPageHtml):
        pagingHTML = housesListPageHtml.find('a', id='next')
        if (pagingHTML):
            return "https:" + pagingHTML.get('href')
        else:
            return ''

    def parseHtmlHouseListPage(self,housesListPageHtml):
        housesHtml = housesListPageHtml.find(class_='tabsContent')
        for summaryHtml in housesHtml.find_all('li'):
            # print('------------------------------')
            moreDetailLink = "https:" + summaryHtml.find('a').get('href')
            house = self.parseHouseHtml(moreDetailLink)

            thumbHtml = summaryHtml.find(class_='lazyload')
            if (thumbHtml):
                house.imageLink = 'http:' + thumbHtml.attrs.get('data-imgsrc')

            self.createOrUpdateHouse(house);

    def extractid(self,href):
        myid = re.search("\d{8,20}", href).group(0)
        return "leboncoin_"+str(myid)

    def parseHouseHtml(self, houseLink):
        house = HouseModel()
        house.source = 'leboncoin'
        house.link = houseLink
        house.id=self.extractid(houseLink)
        oneHouseHtml = BeautifulSoup(urllib.request.urlopen(houseLink), "html.parser")
        itemImageHtml = oneHouseHtml.find(class_='item_image')
        if itemImageHtml:
            if 'empty' not in itemImageHtml.attrs.get('class'):
                house.hasPictures = True

        titleHtml = oneHouseHtml.find('h1')
        if titleHtml: house.title = titleHtml.get_text().strip()

        for lineHtml in oneHouseHtml.find_all(class_='line'):
            propertyHtml = lineHtml.find(class_='property')
            htmlValue = lineHtml.find(class_='value')


            if lineHtml.find_all(class_='ispro'):
                house.isPro = True
            if propertyHtml:
                if propertyHtml.get_text().strip() == 'Prix':
                    priceList = findNumber.findall(trim.sub('',htmlValue.get_text()))
                    if len(priceList): house.price = int(priceList[0])

                if propertyHtml.get_text().strip() == 'Ville':
                    cityList = findAlpha.findall(trim.sub('',htmlValue.get_text()))
                    if len(cityList): house.city = self.normalizeCity(cityList[0])
                    postalCodeList = findNumber.findall(trim.sub('',htmlValue.get_text()))
                    house.postalCode = int(postalCodeList[0])


                if propertyHtml.get_text().strip() == 'Description :':
                    house.description = trim.sub(' ',htmlValue.get_text())

                if propertyHtml.get_text().strip() == 'Type de bien':
                    house.type = trim.sub(' ',htmlValue.get_text()).lower()

                if propertyHtml.get_text().strip() == 'Pièces':
                    house.nbrRooms = int(htmlValue.get_text().strip())

                if propertyHtml.get_text().strip() == 'Surface':
                    surfaceList = findNumber.findall(htmlValue.get_text().replace(" ", ""))
                    if(len(surfaceList)>0):
                        house.surface = int(surfaceList[0])

                if propertyHtml.get_text().strip() == 'GES':
                    house.ges = htmlValue.get_text().strip()[0]

                if propertyHtml.get_text().strip() == 'Classe énergie':
                    house.ces = htmlValue.get_text().strip()[0]
        return house