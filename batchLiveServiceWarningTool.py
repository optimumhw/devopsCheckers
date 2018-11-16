__author__ = 'hal'

import sys
import datetime
import json
import time

import pymssql
import requests
from dogapi import dog_http_api as api


class BatchLiveServiceWarning():

    def __init__( self, logFilePath):

        self.logFilePath = logFilePath
        self.timeOfPostNewEvent = datetime.datetime.now()
        #self.liveServiceWarningAlreadyPosted = False

        self.incidentKey = "LiveServiceWarning"
        self.serviceKey = "96e5fc31c8db4c23ba9959b83b66c6d5"
        self.createEventURI = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        self.headers = {'content-type': 'application/json'}

    def checkDB(self):

        queryString = 'select * from oemvmdata.stage.DataPoint_Live_Stale'
        #queryString = 'select StationName from oemvmdata.stage.DataPoint_Live_Stale'

        conn = pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True)
        cur = conn.cursor()
        cur.execute( queryString )

        rowCount = 0
        rows = []
        for row in cur:
            rowCount += 1
            #print row
            rows.append(row)

        conn.close()

        # rows look like {u'CustomerName': u'Amgen', u'SiteName': u'Thousand Oaks }

        return {'rowCount': rowCount, 'rows': rows}


    def doPostNewIncidentsToPagerDuty(self, listOfStations):

        '''
        payload = '{' + \
        '"service_key":"' + self.serviceKey + '", ' \
        '"incident_key":"' + self.incidentKey + '", ' \
        '"event_type": "trigger",' \
        '"description": "Some sites show stale live data", ' \
        '"client": "Live Service Warning Tool", ' \
        '"details": ' + json.dumps(listOfStations) + ' }'
        '''


        payload = '{' + \
        '"service_key":"' + self.serviceKey + '", ' \
        '"incident_key":"' + self.incidentKey + '", ' \
        '"event_type": "trigger",' \
        '"description": "Some sites show stale live data", ' \
        '"client": "Live Service Warning Tool", ' \
        '"details": ' + json.dumps(listOfStations) + ' }'

        self.logMessage('Posting new incident: ' + payload )
        r = requests.post(self.createEventURI, headers=self.headers, data=payload)
        self.logMessage("post status: " + str(r.status_code))

        if r.status_code != 200 :
            self.logMessage("oops...error: " + str(r.json()))
        

    def doPostResolvesToPagerDuty( self, staleDurationStr ):

        payload = '{' + \
        '"service_key":"' + self.serviceKey + '", ' \
        '"incident_key":"' + self.incidentKey + '", ' \
        '"event_type": "resolve",' + \
        '"description": "No live service warnings",' + \
        '"client": "Live Service Warning Tool",' + \
        '"details": { "Problem": "fixed","Duration stale": "' + staleDurationStr + '" }' + \
        '}';

        self.logMessage("posting RESOLVED: " + payload)

        r = requests.post( self.createEventURI, data=payload, headers=self.headers )
        self.logMessage("post status: " + str( r.status_code ))
        if r.status_code != 200:
            self.logMessage("oops...error: " + str( r.json() ))

    def postToDataDog(self, num ):

        api.api_key = 'fe1cd13de75c73f4f4de29acd85c4b36'
        api.application_key = 'd0a1be7f8d3d141c8adda765ceb41f90422cbcda'
        metricName = 'foobar.liveServiceDown.numStations'

        self.logMessage("posting to DataDog: " + metricName + " = " + str(num))
        
        api.metric(metricName, num)

    def getStations(self, queryResults):
        stations = []
        for row in queryResults :
            if not self.isWhiteListed( row['StationName']):
                val = "Name:%s SuperId:%s Addr:%s" % (row['StationName'], row['SupervisorID'], row['BaseAddressHistory'] )
                stations.append(val);
        return stations

    def isWhiteListed(self,stationName):
        whiteList = []
        whiteList.append('OE_J140023_JJ_Janssen_Ortho_Manati')
        whiteList.append('OE_J150025_WakeForest_NorthPlant')
        #whiteList.append('OE_J140044_Alcon_OCP')
        if stationName in whiteList:
            self.logMessage("White listed: " + stationName)
            return True
        return False

    def loop(self):

        self.logMessage('getting query results')
        queryResults = self.checkDB()

        stations = self.getStations(queryResults['rows'])
        count = len(stations)

        #post the metric (# of stations w/ live service problems) to dataDog
        self.postToDataDog( count )

        #post to pager duty if not already posted
        #if count > 0 and not self.liveServiceWarningAlreadyPosted:
        if count > 0:
            self.timeOfPostNewEvent = datetime.datetime.now()
            self.doPostNewIncidentsToPagerDuty(stations)
            #self.liveServiceWarningAlreadyPosted = True  # set this after post in case of timeout exception during post

        #post resolves
        #elif count == 0 and self.liveServiceWarningAlreadyPosted is True:
        else:
            staleDuration = datetime.datetime.now() - self.timeOfPostNewEvent
            staleDurationStr = self.getTimeDeltaAsString( staleDuration )
            self.doPostResolvesToPagerDuty( staleDurationStr )
            #self.liveServiceWarningAlreadyPosted = False

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

    if len(sys.argv) < 2:
        print 'usage: python batchLiveServiceWarningTool.py logfilepath'
        sys.exit(0)

    batchChecker = BatchLiveServiceWarning(sys.argv[1])
    while True:
        try:
            batchChecker.loop()
        except Exception, e:
            print e
            pass
        time.sleep(60 * 60 * 4) #sleep for 4 hours
        #time.sleep( 20 ) #sleep for 20 seconds




'''
curl -H "Content-type: application/json" -X POST -d '{"service_key":"96e5fc31c8db4c23ba9959b83b66c6d5", "incident_key":"SHW-Amgen-Thousand-Oaks", "event_type": "trigger","description": "Amgen-Thousand Oaks has stale histories", "client": "Stale History Warning Tool", "details": { "alert type": "stale histories" } }' "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
'''

'''
(select distinct SiteID  from oemvm.dim.vwAlertAllList
    where AlertID = 2 or AlertID = 7 --or AlertID = 14 ) ,

StaleHistoryIDs as ( Select distinct SiteID
from [oemvm].[dim].[vwAlertAllList] where AlertID = 12 ) ,

FinalIDs as ( Select  m.SiteID from StaleHistoryIDs m except select n.SiteID from NiagaraNetworkDownIDs n )

select c.Name CustomerName, s.ShortName SiteName
from FinalIDs f, oemvm.dim.Customer c, oemvm.dim.Site s

where f.SiteID = s.SiteID and s.CustomerID = c.CustomerID
'''