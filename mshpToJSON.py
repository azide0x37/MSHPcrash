import urllib2
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
"""
class dlData:
    def __init__(self):
        self.url = 'http://www.mshp.dps.missouri.gov/HP68/search.jsp'

    def __str__(self):
        try:
            return self.url
        except:
            print "Unable to print url." 

    def Scrape(self):
        opener = urllib2.build_opener()
       opener.addheaders = [('User-agent', 'Mozilla/5.0')] 
        response = opener.open(self.url)
                
        #take HTML and strip out the tables into a dict that perserves ordering
        self.data = response.read()
        response.close()
        souped = BeautifulSoup(self.data)

        #resp = [[cell.text for cell in row("td")] for row in BeautifulSoup(self.data)("tr")]
        tables = souped.find('body').find_all('table', recursive=False)
        print len(tables)
        print tables[0].text.strip()
        
        
        
        #self.resp = json.dumps(OrderedDict(resp))
        #print self.resp
        print self.data
        
parse = dlData()
parse.Scrape()
"""
opener = urllib2.build_opener()

#Use a proper useragent to evade the anti-hack software
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
response = opener.open('http://www.mshp.dps.missouri.gov/HP68/search.jsp')
soupdata = response.read()

datasoup = BeautifulSoup(soupdata)

#This is the particular table with the data we need. Find a better way to pick the right one?
table = datasoup.find('table', summary="Table listing details of the accident.")

rows = table.findAll('tr')

col_names = ['Name', 'Age', 'Hometown', 'Severity', 'Date', 'Time', 'County', 'Location', 'Troop']

dataset = []

for tr in rows:
    cols = tr.findAll('td')
    #print cols
    row_data = OrderedDict()
    counter = 0

    for td in cols[1:]:
        #if counter == 0:
            #continue
        #print td
        text = ''.join(td.find(text=True))
        #print text# + ",",

        try:
            row_data[col_names[counter]] = text
            counter += 1
        except:
            counter = 0
            continue
    
    """
    try:
        row_data.pop(0)
    except:
        continue
    """
    dataset.append(row_data)
    #print
#for row in dataset:
#    print row

formatted = json.dumps(dataset, indent=4, separators=(',',':'))
print formatted


