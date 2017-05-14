import yahoo_finance as yfn
#from DelniceWebApp.models import *
import pandas as pd
from pyquery import PyQuery
from countries import countries

class Company():

    def __init__(self, ticker, preexisting, ipo = None, sector = None, industry = None):
        self.tickerSymbol = ticker
        self.stockArray = None
        self.handlesSet = False
        self.sector = sector
        self.industry = industry
        self.ipo = ipo
        self.dataLoaded = preexisting

#add exceptions and consider updating all data at every querry
    def update(self):
        try:
            #access to yahoo querry language library
            self.stockHandle = yfn.Share(self.ticker)
            #access to django class
            self.djangoPodjetje = Podjetje()
            self.djangoDelnica = Delnica()

            self.handlesSet = True
        except:
            print("Setting handles failes")


        if not self.dataLoaded and self.handlesSet:
            try:
                self.djangoPodjetje.simbol = self.tickerSymbol
                self.djangoPodjetje.polnoIme = self.stockHandle.get_name()
                self.djangoPodjetje.lokacija = self.getLocation()
                if self.sector:
                    self.djangoPodjetje.sektor = self.sector
                if self.industry:
                    self.djangoPodjetje.industrija = self.industry
                if self.ipo:
                    self.djangoPodjetje.ipo = self.ipo

                self.djangoPodjetje.save()
            except:
                print("Loading data failed")
                return
            self.dataLoaded = True
            self.lastStockDate = None
        else:
            pass
            self.lastKnownDate = self.djangoDelnica.objects.filter(simbol = self.tickerSymbol).latest(datum).datum

    def getLocation(self):
        """Retrieves country data from yahoo finance webpage and extracts country"""

        url = "https://finance.yahoo.com/quote/{}/profile?p={}".format(self.tickerSymbol, self.tickerSymbol)

        pq = PyQuery(url)
        #company data happens to be the first paragraph on the page
        info = pq('p:first').text()

        info = info.split(" ")
        webAddr = info.pop()
        while info[-1][-1].isdigit():
            info.pop()
        for i in range(1, len(info)):
            if " ".join(info[-i:]) in countries:
                country = " ".join(info[-i:])
                # address = " ".join(info[:-1])

        return country


def convertMarketCap(capString):
    """Converts string representation of market capitalisation to integer"""
    # not interested in sub million companies
    coeficient = 0
    try:
        if capString[-1] == "T":
            #short scale meaning (data source is US based)
            coeficient = 10**12
        elif capString[-1] == "B":
            coeficient = 10**9
        elif capString[-1] == "M":
            coeficient = 10**6

        return int(float(capString[1:-1]) * coeficient)
    except:
        #not interested in incorrectly defined companies
        return 0


def getExistingCompanies():
    """Retrieves present companies from database"""
    pass

#sort out exception handling
def getTopCompanies(companyDict, N=500):
    """Retrieves list of companies from NASDAQ website and adds top N to dataset"""

    nasdaqURL = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download"
    nyseURL = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"

    # ['Symbol', 'MarketCap', 'IPOyear', 'Sector', 'industry']
    try:
        nasdaq = pd.read_csv(nasdaqURL, sep = ",", header = 0, usecols = [0,3,4,5,6])
        nyse = pd.read_csv(nyseURL, sep=",", header = 0, usecols = [0,3,4,5,6])
        nasdaq.set_index('Symbol')
        nyse.set_index('Symbol')
    except:
        print("csv retrieval failed")
        return None


    companies = pd.concat([nyse, nasdaq], verify_integrity=True, ignore_index=True)
    companies['MarketCap'] = companies['MarketCap'].map(lambda s : convertMarketCap(s))
    companies = companies.sort_values(by=["MarketCap"], ascending=False)



    for i in companies[:N].itertuples():
        if i[1] not in companyDict:
            companyDict[i[1]] = Company(i[1], False, ipo = i[3], sector = i[4], industry=i[5])
            companyDict[i[1]].update()

    return companyDict

getTopCompanies({})

#GET EXISTING SHARES FROM DATABASE

#SCRUB TOP n COMPANY NAMES

#GET COMPANY DATA

#PUSH COMPANY DATA INTO DATABASE
