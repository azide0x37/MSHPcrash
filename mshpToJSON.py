import urllib2
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import pandas as pd

class mshpScraper:
    
    def __init__(self,
            url = 'http://www.mshp.dps.missouri.gov/HP68/SearchAction', 
            colNames = ['Name', 'Age', 'Hometown', 'Severity', 'Date', 'Time', 'County', 'Location', 'Troop']), 
            county = 'Jefferson'):
        
        self.url = url
        self.colNames = colNames
    


    def __str__(self):
        try:
            return self.url
        except:
            print "Unable to print url." 

    def __call__(self):
        opener = urllib2.build_opener()
        

        #Use a proper useragent to evade the anti-hack software
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = opener.open(self.url)
        webpage = response.read()
        webpageSouped = BeautifulSoup(webpage)

        #This is the particular table with the data we need.
        #TODO: Find a better way to pick the right one?
        table = webpageSouped.find('table', summary="Table listing details of the accident.")
        rows = table.findAll('tr')

        #TODO: Pull colNames ftom the table headngs
        dataset = []
        
        for tr in rows:
            cols = tr.findAll('td')
            row_data = OrderedDict()
            counter = 0

            #TODO: the zeroth element of cols is null; why? Fix.
            for td in cols[1:]:
                text = ''.join(td.find(text=True))
                try:
                    row_data[self.colNames[counter]] = text
                    counter += 1
                except:
                    counter = 0
                    continue
            dataset.append(row_data)

        formatted = json.dumps(dataset, indent=4, separators=(',', ':'))
        #print formatted
        return pd.DataFrame(dataset)

myScrape = mshpScraper()
#adding __call__ method allows me to call the instance as a function! Neat!
#TODO: find out if this is a good or bad practice

dfScrape = pd.DataFrame(myScrape())

#print dfScrape.sum(axis = 2)
#print dfScrape.mean(axis = 2)
print dfScrape
