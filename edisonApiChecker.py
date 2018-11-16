__author__ = 'hal'

'''
EdisonAPIChecker - Checks once / hour and posts info to pager duty when:

    The api fails to return equipment for:
        custID = 'att'
        siteID = 'wb3090'
        installationID = 'wb3090lp'
        stationID = 'oe_j150041_atth_jefferson_tx'

    Also if the api fails to return time-series data (last day) for all this site-data-points (see below for the list)

'''

import sys
import datetime
import json
import os
import time
import urllib

import pymssql
import requests


class EdisonAPIChecker():

    def __init__( self, logFilePath, host, username, password ):

        self.logFilePath = logFilePath
        self.HOST = host
        self.VERSION = '2015.10'
        self.USERNAME = username
        self.PASSWORD = password

        self.OEURL = self.HOST + '/api/' + self.VERSION

        self.token = ""


        self.incidentKey = "EdisonAPIDown"
        self.serviceKey = "96e5fc31c8db4c23ba9959b83b66c6d5"
        self.createEventURI = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        self.headers = {'content-type': 'application/json'}


    def getToken(self ):

        url = self.OEURL + '/oauth/token'

        headers = {}
        headers['content-type'] = 'application/json'

        dict = {}
        dict['grant_type'] = 'password'
        dict['username'] = self.USERNAME
        dict['password'] = self.PASSWORD

        payload = json.dumps(dict)
        r = requests.post(url, data=payload, headers=headers)
        dict = json.loads(r.text)

        if r.status_code == 200:
            self.token = dict['access_token']
            r.status_code, self.token
        else:
            self.token = '?'

        return r.status_code, 'failed to get the auth token'


    # ========== API SERVICE =================


    def getListOfSites(self, custSid):

        url = self.OEURL + '/' + custSid + '/site'

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to get list of sites'


    def getEquipmentInfo(self, sid, equipmentType, dataPoints, includeAlarmsFlag ):

        url = self.OEURL + '/' + sid + '/' + equipmentType

        if len(dataPoints) > 0 or includeAlarmsFlag:
            url += '?'

        if includeAlarmsFlag :
            url += 'alarms=' + 'true'

        if len( dataPoints) > 0 :
            url += '&datapoints=' + dataPoints

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to get equipment info'



    def getTimeSeriesData(self, sid, startTime, endTime, dataPointList):

        paramDict = {}
        paramDict['start'] = startTime
        paramDict['end'] = endTime
        paramDict['datapoints'] = ','.join(dataPointList)

        url = self.OEURL + '/' + sid + '/?' + urllib.urlencode( paramDict )


        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token

        r = requests.get( url, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)
        return r.status_code, 'failed to get time series data'


    def postQueriesForTimeSeriesData(self, sid, postBodyDict ):

        url = self.OEURL + '/' + sid + '/datapoints'

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token

        payload = json.dumps(postBodyDict)

        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to post multi-part query'


    def getSpWho2Info(self):

        with pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True) as conn:
            with  conn.cursor() as cur:
                cur.callproc( 'sp_who2' )
                rows = []
                for row in cur:
                    jsonRowString = json.dumps(row)
                    jsonRow = json.loads( jsonRowString )
                    rows.append( jsonRow )
        return rows



    def loop(self):

        status, msg = self.checkAPI()

        if status != 200:

            sp_who2_output_rows = []
            try:
                #get sp_who2 info
                #sp_who2_output_rows = self.getSpWho2Info()
                pass
            except Exception, e:
                self.logMessage('could not get sp_who2 results')
                self.logMessage( e )
                pass

            payload = 'http status code: ' + str(status) + ' - ' + msg

            self.doPostNewIncidentsToPagerDuty( payload,  sp_who2_output_rows )

        else:
            todaysDate = datetime.datetime.now()
            someTimeStamp = datetime.datetime.strftime( todaysDate, '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            self.logMessage( someTimeStamp + " and all is well")


    def checkAPI(self):

        custID = 'att'
        siteID = 'wb3090'
        installationID = 'wb3090lp'
        stationID = 'oe_j150041_atth_jefferson_tx'

        chillerTwoName = 'chiller2'

        custSid = 'c:' + custID
        siteSid = custSid + '.s:' + siteID
        instSid = siteSid + '.i:' + installationID
        stationSid = instSid + '.st:' + stationID

        chiller2EquipSid = stationSid + '.e:' + chillerTwoName

        todaysDate = datetime.datetime.now()

        endDate = todaysDate.replace( hour=0, minute=0, second=0, microsecond=0)
        startDate = endDate - datetime.timedelta(days=1)

        start = datetime.datetime.strftime( startDate, '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end = datetime.datetime.strftime( endDate , '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        site_data_points = ["BASMode",
            "ChilledWaterDifferentialPressure","ChilledWaterPlantRequired","ChilledWaterReturnTemp",
            "ChilledWaterSupplyTemp","ChilledWaterTotalFlow","ChillerEfficiency","ChillerWaterSupplyTempSetPoint",
            "CondenserWaterReturnTemp","CondenserWaterSupplyTemp","FollowingSetPoints","OptimizationRequired",
            "OptimumControl","OutsideAirHumidity","OutsideAirTemp","OutsideAirWetBulbTemp","PlantReady",
            "TotalChillerkW","TotalCondenserWaterPumpkW","TotalCoolingTowerFankW","TotalPlantEfficiency",
            "TotalPlantTons","TotalPlantkW","TotalPrimaryChillerWaterPumpkW",
            "TotalSecondaryChillerWaterPumpkW"]


        all_datapoints = '*'
        includeAlarmsFlag = 'true'

        # 1.) Authenticate
        status, oauthToken = self.getToken()
        if status != 200:
            return status, 'failed to get token'

        # 2.) Get list of sites
        status, sites = self.getListOfSites( 'c:' + custID )
        if status != 200:
            return status, 'failed to get sites'

        # 3.) Get equipment info for one of the sites
        status, equipInfo = self.getEquipmentInfo( siteSid, 'chiller', all_datapoints, includeAlarmsFlag )
        if status != 200:
            return status, 'failed to get chiller equipment info'

        # 4.) Get time series data
        status, seriesData = self.getTimeSeriesData( chiller2EquipSid, start, end, site_data_points )
        if status != 200:
            return status, 'failed to get time series data'

        #all done
        return status, "OK"


    #===============================

    def doPostNewIncidentsToPagerDuty( self, msg, sp_who2_rows) :

        msg2 = '"sp_who2_output":' + json.dumps(sp_who2_rows)

        payload = '{' + \
        '"service_key":"3fd18d12de5b49a2b2e8cfbcb7b9c6e4", ' \
        '"incident_key":"' + self.incidentKey + '", ' \
        '"event_type": "trigger",' \
        '"description": "' + msg +'", ' \
        '"client": "API Checker", ' \
        '"details": { ' \
                '"alert type": "' + msg + '",' + msg2 + '} }'

        uri = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        headers = {'content-type': 'application/json'}

        self.logMessage( 'Posting new incident: ' + payload )


        r = requests.post( uri, headers=headers, data=payload )
        self.logMessage( "post status: " + str( r.status_code ) )

        if r.status_code != 200:
            self.logMessage( "oops...error: " + str( r.json() ) )


    def getTimeDeltaAsString(self, td ):
        hours, remainder = divmod( td.seconds, 3600 )
        minutes, seconds = divmod( remainder, 60 )
        td_formatted = '%s:%s:%s' % (hours, minutes, seconds )
        return td_formatted

    def logMessage(self, msg):
        f = open(self.logFilePath, 'a')
        f.write(msg + "\n")
        f.close

if __name__ == '__main__':

        if len(sys.argv) < 2 :
            print 'usage: python edisonApiChecker.py logfilepath'
            sys.exit(0)

        username = os.environ['TESTUSER'].strip()
        password =  os.environ['TESTUSERPASSWORD'].strip()

        host = 'https://opticx.optimumenergyco.com'

        apiChecker = EdisonAPIChecker( sys.argv[1], host, username, password )
        while( True ) :
            try:
                apiChecker.loop()
            except Exception, e:
                print e
                pass
            time.sleep( 60 * 60 * 1 ) #sleep for 1 hours
            #time.sleep( 20 ) #sleep for 20 seconds


