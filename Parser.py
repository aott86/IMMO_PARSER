from abc import ABC, abstractmethod
import pdfkit
import re
import sys
import logging

from HouseDao import HouseDao

class Parser(ABC):
    @abstractmethod
    def getNextPageUrl(self, html):
        pass

    @abstractmethod
    def parseHtmlHouseListPage(housesListPageHtml):
        pass

    def __init__(self):
        self.logger = logging.getLogger("IMMO_PARSER")
        self.pdfKitConfig = pdfkit.configuration(
            wkhtmltopdf=bytes(sys.argv[1], 'utf-8'))
        self.houseDao = HouseDao();

    def createNewHouse(self,house):
        self.houseDao.insertHouse(house)
        try:
            pdfkit.from_url(house.link, "out.pdf", configuration=self.pdfKitConfig)
            pdf = pdfkit.from_url(house.link, False, configuration=self.pdfKitConfig)
            self.houseDao.addPdf(house.id, pdf)
        except IOError:
            self.logger.exception ('ERROR generating pdf for house '+str(house.id))

    def createOrUpdateHouse(self,house):
        self.logger.info(house.title)
        if house.isHouse():
            self.logger.info(house.city+"\t"+str(house.price)+"\t"+str(house.id))
            result = self.houseDao.updateHouseParsed(house);

            # If exists
            if result['n'] == 0:
                self.logger.info("NEW " + str(house.id))
                self.createNewHouse(house)

    def normalizeCity(self,cityName):
        cityName = re.sub('[^a-zA-Z- ]', '', cityName)
        cityName = cityName.replace(" ", "-")
        cityName = cityName.upper()
        return cityName