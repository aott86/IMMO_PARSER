# IMMO_PARSER
Couple of parser for best known real-estate websites

## HouseExtractor.py
Main class to run:
* HouseExtractor.py  mongodb-host mongodb-port path-to-config-file
* ex: python3.4 HouseExtractor.py localhost 27017 ./conf.txt

### conf.txt
Contains a list of url to parse. One url by line.
The web site's domain will indicates which parser to use.
Supported web sites domains:
https://www.leboncoin.fr/
http://www.logic-immo.com/
http://www.explorimmo.com/

Examples can be found in the conf folder.