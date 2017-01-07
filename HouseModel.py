import re
from datetime import datetime

class HouseModel:
    def __init__(self):
        self.id = None
        self.link = ''
        self.title = ''
        self.price = 0
        self.surface = 0
        self.hasPictures = False
        self.isPro = False
        self.city = ''
        self.postalCode = 0
        self.state = ''
        self.nbrRooms = 0
        self.ges = ''
        self.ces = ''
        self.type = ''
        self.imageLink = ''
        self.source = ''
        self.deleted = False


    def toStr(self):
        if self.link: print ('link:'+self.link)
        if self.title: print ('title:'+self.title)
        if self.price: print ('price:'+str(self.price))
        if self.surface: print ('surface:'+str(self.surface))
        if self.hasPictures: print ('hasPictures:'+str(self.hasPictures))
        if self.isPro: print ('isPro:'+str(self.isPro))
        if self.city: print ('city:'+self.city)
        if self.postalCode: print ('postalCode:'+str(self.postalCode))
        if self.state: print ('state:'+self.state)
        if self.nbrRooms: print ('nbrRooms:'+str(self.nbrRooms))
        if self.ges: print ('ges:'+self.ges)
        if self.ces: print ('ces:'+self.ces)
        if self.imageLink: print ('imageLink:'+self.imageLink)
        if self.description: print ('description:'+self.description)
        if self.deleted: print ('deleted:'+self.deleted)
        if self.source: print ('source:'+self.source)
        if self.price and self.surface: print('m2price_last'+self.getM2Price())

    def keys(self):
        return ['link','title','price','surface','hasPictures','isPro','city','postalCode', 'state','nbrRooms','ges','ces','imageLink','description','type', 'deleted','source','m2price_last']

    def item(self):
        dateNow=datetime.now();
        return {'_id': self.id,'link':self.link,'title':self.title,'price_init':self.price, 'price_last':self.price, 'date_init':dateNow,'date_last':dateNow, 'surface':self.surface,'hasPictures':self.hasPictures,'isPro':self.isPro,'city':self.city,'postalCode':self.postalCode, 'state':self.state,'nbrRooms':self.nbrRooms,'ges':self.ges,'ces':self.ces,'imageLink':self.imageLink, 'description':self.description, 'type':self.type, 'deleted':self.deleted,'source':self.source, 'm2price_last':self.getM2Price()}

    def isHouse(self):
        if re.search('^appartement', self.title, re.IGNORECASE):
            return False
        if re.search('^terrain', self.title, re.IGNORECASE):
            return False
        elif re.search('^beau terrain', self.title, re.IGNORECASE):
            return False
        else:
            return True

    def getM2Price(self):
        return round((self.price / self.surface))