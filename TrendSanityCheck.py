PSEUDO___author__ = 'hal'

import json
import urllib

import requests


class TrendAPIs():

    def __init__( self, db, username, password ):
        self.USER = username
        self.PASSWORD = password

        if db == "PROD" :
            self.AUTH_ENDPOINT = "https://opticx.optimumenergyco.com/api/2015.10/"
            self.SERVICE_ENDPOINT = "https://opticx.optimumenergyco.com/api/2015.10/"
            self.AUD = "urn:optimumenergy-mobi:mobile"
            self.MOBILE_HEALTH_URL = "https://opticx.optimumenergyco.com/api/2015.10/trend/health"

        elif db == "STAGE" :
            self.AUTH_ENDPOINT = "https://stage.oeprod.us/api/2015.10/"
            self.SERVICE_ENDPOINT = "https://stage.oeprod.us/api/2015.10/trend/"
            self.AUD = "urn:optimumenergy-mobi:mobile"
            self.MOBILE_HEALTH_URL = "https://stage.oeprod.us/api/2015.10/trend/health"

        else:
            raise Exception( "db type is unsupported. Use 'PROD' or 'STAGE' ")



    #=============== HELPERS ==================
    def getSessionToken( self ):
        url = self.AUTH_ENDPOINT + "oauth/token"

        headers = {}
        headers['content-type'] = 'application/x-www-form-urlencoded'

        dict = {}
        dict['username'] = self.USER
        dict['password'] = self.PASSWORD
        dict['scope'] = 'read+write'
        dict['grant_type']='password'

        payload = urllib.urlencode(dict)
        r = requests.post(url, data=payload, headers=headers)
        dict = json.loads( r.text )

        return dict['access_token']

    def getServiceHeaders( self ) :
        token = self.getSessionToken()
        bearer_token = "bearer " + token
        headers = {'content-type': 'application/json', 'Authorization' : bearer_token }
        return headers

    #========= API wrappers ======================
    def mobileHealthCheck( self ) :
        url = self.MOBILE_HEALTH_URL

        headers = {'content-type': 'application/json'}
        r = requests.get( url, headers=headers )

        return r.status_code


    def getCompanies( self ):
        url = self.SERVICE_ENDPOINT + "companies"
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        companies = dict["companies"]
        return r.status_code, companies

    def getCompanyOverview( self, uuid ):
        url = self.SERVICE_ENDPOINT + "company-overview?uuid=" + uuid
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        return r.status_code, dict

    def getSiteOverview( self, uuid, timeframe ):
        url = self.SERVICE_ENDPOINT + "site-overview?uuid=" + uuid + "&timeframe=" + timeframe
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        return r.status_code, dict

    def getSiteTrends( self, uuid, trendType, timeframe ):
        args = "site-trends?uuid=%s&trend=%s&timeframe=%s" % ( uuid, trendType, timeframe )
        url = self.SERVICE_ENDPOINT + args
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        return r.status_code, dict


    def getReps( self, uuid ):
        args = "reps?uuid=%s" % ( uuid )
        url = self.SERVICE_ENDPOINT + args
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        return r.status_code, dict


    def getSiteReports( self, uuid ):
        #args = "site-reports?uuid=%s" % ( uuid )
        args = "site-reports"
        url = self.SERVICE_ENDPOINT + args
        print "*URL= ", url
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        return r.status_code, dict

    def getReport( self, reportId ):
        #args = "report?reportId=%s" % reportId
        args = "report"
        url = self.SERVICE_ENDPOINT + args
        print "*URL= ", url
        r = requests.get( url, headers=self.getServiceHeaders() )
        dict = json.loads( r.text )
        return r.status_code, dict


#=========================================================

if __name__ == '__main__' :

    timeframes = ["year", "month", "week", "today"]
    trendNames = [ "savings", "plant", "optimization", "chiller", "key" ]

    #db = sys.argv[1]
    #username = sys.argv[2]
    #password = sys.argv[3]

    db = 'STAGE'
    username = 'hal.prod.testuser'
    password = 'abcd#01'

    restClient = TrendAPIs( db, username, password )

    token = restClient.getSessionToken()
    print "token: ", token

    status = restClient.mobileHealthCheck()
    print "mobile health is: ", status

    status, companies = restClient.getCompanies()
    print "status : ", status
    if status == 200:
        print "Number of companies: ", len( companies )


    print 'Companies:'

    for company in companies :
        print 'Company uuid:', company['uuid'], company['name']

        status_code, companyOverview = restClient.getCompanyOverview( str(company['uuid']) )
        if( status_code != 200 ):
            print 'status_code', str(status_code), 'Could not get overview for:', company['uuid'], '-', company['name']
            continue

        #print json.dumps( companyOverview )

        co = companyOverview['overview']
        savings = co['savings']

        print '  Efficiency Average:', co['efficiencyAverage'], 'EffAvg Delta:', co['efficiencyAverageDelta']
        print '  Savings:'
        print '    Money:', savings['moneySaved']
        print '    Energy:', savings['energySaved']
        print '    CO2:', savings['co2Saved']
        print '    Saved Since:', savings['since']

        op = co['optimizationGraph']
        print '  Optimization Graph: Not:', op['not'], 'Full:', op['full'],  'Part:', op['partial'],  'CommFailure:', op['commFailure']

        print '  Sites:'

        sites = companyOverview['sites']

        for site in sites:

            #print json.dumps( site )

            print '    uuid:', site['uuid'], 'Site Short Name:', site['shortName'], 'Site Long Name:', site['name']
            print '    Optimization Status:', site['optimizationStatus']
            print '    Site Savings:', site['savings'], 'Efficiency Avg:', site['efficiencyAverage'], 'Delta:', site['efficiencyAverageDelta']

            weather = site['weather']

            if 'temperature' in weather:
                tempDegrees = str(weather['temperature'])
                temperature = str( tempDegrees )
            else:
                temperature = 'not present'

            if 'condition' in weather:
                condition = weather['condition']
            else:
                condition = 'not present'

            print '    Weather - Temp:', temperature, 'Condition:', condition




            sos= {}

            for timeframe in timeframes:

                #print '  Site overview for timeframe: ', timeframe

                status_code, sos[timeframe] = restClient.getSiteOverview( site['uuid'], timeframe )
                if status_code != 200:
                    print status_code, 'could not get site overview for:', site['uuid'], ' for Timeframe:', timeframe
                    continue

                #print json.dumps(sos[timeframe])

            '''
            for timeframe in timeframes:
            sosByTimeFrame[timeframe]['plantEfficiency']
            print 'avg temp:', so['avgTemperature']
            print 'isChillerDiagnosticSite?:', so['isChillerDiagnosticSite']
            print 'energyConsumed:', so['energyConsumed']
            '''




            #sg = "    %30s %15s %15s %15s %15s" % ('.........1..........2.........', 'today', 'week', 'month', 'year')
            msg = "    %34s %15s %15s %15s %15s" % ('Site Overview Datails         ', 'Today', 'Week', 'Month', 'Year')
            print msg

            fields = ['plantEfficiency', 'avgTemperature', 'energyConsumed',
                      'peakConsumption', 'tonHoursProduced', 'chillerEfficiency' ]

            for field in fields:
                msg = "        %-30s %15.3f %15.3f %15.3f %15.3f" % (
                                                        field,
                                                        sos['today'][field],
                                                        sos['week'][field],
                                                        sos['month'][field],
                                                        sos['year'][field] )

                print msg



            fields = ['co2Saved','energySaved','moneySaved']
            for field in fields:
                msg = "       %-30s %15.3f %15.3f %15.3f %15.3f" % (
                                        field,
                                        sos['today']['savings'][field],
                                        sos['week' ]['savings'][field],
                                        sos['month']['savings'][field],
                                        sos['year' ]['savings'][field] )
                print msg


            print()
            for trend in trendNames:
                for timeframe in timeframes:
                    status, dict = restClient.getSiteTrends( site['uuid'], trend, timeframe )

                    print( json.dumps( dict ))
                    print()













