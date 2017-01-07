from Parser import Parser
from HouseModel import HouseModel
from bs4 import BeautifulSoup
import urllib
import re

trim = re.compile(r'\s+')
findNumber = re.compile(r'([0-9]{1,10})')
findAlpha = re.compile('[a-zA-Z -]+')

class SeLogerParser(Parser):
    def getNextPageUrl(self, housesListPageHtml):
        pagingHTML = housesListPageHtml.find(class_='pagination_next')
        if (pagingHTML):
            return pagingHTML.attrs.get('href')
        else:
            return ''

    def parseHtmlHouseListPage(self,housesListPageHtml):
        print('Parse seloger immo house list')
        for summaryHtml in housesListPageHtml.find_all('article'):
            # print('------------------------------')
            moreDetailLink = summaryHtml.find('a').attrs.get('href')
            house = self.parseHouseHtml(moreDetailLink)

            thumbHtml = summaryHtml.find(class_='slidesjs-control')
            if (thumbHtml):
                house.imageLink = thumbHtml.find('img').attrs.get('src')

            #self.createOrUpdateHouse(house)

    def parseHouseHtml(self, houseLink):
        house = HouseModel()
        house.source = 'seloger'
        house.link = houseLink
        house.isPro = True
        oneHouseHtml = BeautifulSoup(urllib.request.urlopen(houseLink), "html.parser")

        idHtml = oneHouseHtml.find(class_='main')
        if idHtml:
            house.id = "seloger_"+idHtml.attrs.get('data-listing-id')

        itemImageHtml = oneHouseHtml.find(class_='carrousel_image_visu')
        if itemImageHtml:
            house.hasPictures = True

        titleHtml = oneHouseHtml.find('h1')
        if titleHtml:
            house.title = titleHtml.get_text().strip()

        typeHtml = oneHouseHtml.find(class_='offer-type')
        if typeHtml:
            house.type = 'maison'

        priceHtml = oneHouseHtml.find(id='price')
        if priceHtml:
            house.price = int(findNumber.findall(trim.sub('',priceHtml.get_text()))[0])

        formContactHtml = oneHouseHtml.find(class_='form-contact')
        if formContactHtml:
            inputFormlist =formContactHtml.find_all('input')
            for inputForm in inputFormlist:
                if inputForm.attrs.get('name') == 'ville':
                    house.city=self.normalizeCity(inputForm.attrs.get('value'))
                elif inputForm.attrs.get('name') == 'codepostal':
                    house.postalcode = int(inputForm.attrs.get('value'))
                elif inputForm.attrs.get('name') == 'surface':
                    house.surface=int(inputForm.attrs.get('value'))
                elif inputForm.attrs.get('name') == 'price':
                    house.surface=int(findNumber.findall(inputForm.attrs.get('value').strip())[0])
                elif inputForm.attrs.get('name') == 'typebien':
                    house.type = inputForm.attrs.get('value').strip()
                elif inputForm.attrs.get('name') == 'description':
                    house.description = inputForm.attrs.get('value').strip()

        dpegesHtml = oneHouseHtml.find_all(class_='item-dpeges')
        for dpeorgesHtml in dpegesHtml:
            dpeorges = dpeorgesHtml.attrs.get('title')
            if 'DPE' in dpeorges:
                house.ces = dpeorges[5:6]
            elif 'GES' in dpeorges:
                house.ges = dpeorges[5:6]

        criterionsHtml = oneHouseHtml.find(class_='criterions')
        if criterionsHtml:
            criteriaListHtml = criterionsHtml.find_all('li')
            for criteriaHtml in criteriaListHtml:
                if 'Pièces' in criteriaHtml.get_text().strip():
                    house.nbrRooms = int(findNumber.findall(trim.sub('', criteriaHtml.get_text().strip()))[0])

        return house