__author__ = 'hal'

import sys
import datetime
import json
import time

import pymssql
import requests
from dogapi import dog_http_api as api

class BatchStaleHistoryWarning():

    def __init__( self, logFilePath):

        self.logFilePath = logFilePath

        self.timeOfPostNewEvent = datetime.datetime.now()

        self.incidentKey = "StaleHistories"
        self.serviceKey = "96e5fc31c8db4c23ba9959b83b66c6d5"
        self.createEventURI = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        self.headers = {'content-type': 'application/json'}
        self.apiKey = 'VWoKkL-NYFBnzj364Nx7'


    def getWhiteList(self):

        whiteList = []

        whiteList.append(345) #CEPMMelia2
        #whiteList.append(361) #CEPMRoyltn
        whiteList.append(370) #CEPMMelCIR
        whiteList.append(342) #JJCrkB2
        whiteList.append(319) #BrynMawrPA
        whiteList.append(160) #EthiconNM
        whiteList.append(426) #all three Bank of America stations
        whiteList.append(396) #SchaffB49
        whiteList.append(361) #CEPMRoyltn
        whiteList.append(446) #MCormkHV
        whiteList.append(350) #RaritanLP
        whiteList.append(420) #vIntel-VietnamCUiB
        whiteList.append(323) #db-05
        whiteList.append(58)  #winnepeg hsc
        whiteList.append(486) #micron
        whiteList.append(368) #reading
        whiteList.append(378) #greenwich lane
        whiteList.append(159)  # VA Portland
        whiteList.append(487)  # Intel RioRancho
        whiteList.append(296)  # Cleaveland Clinic
        whiteList.append(508) #3TimesSQ
        whiteList.append(24) #ThousandOaks
        whiteList.append(476) #VisionHNGZ

        list = str(whiteList).strip('[]')

        return list

    def checkDB(self):


        # old_queryString = '''
        #
        # ;with
        # NiagaraNetworkDownIDs as (
        #     select distinct SiteID  from oemvm.dim.vwAlertAllList
        #     where AlertID = 2 or AlertID = 7 or AlertID = 14 or AlertID = 11
        #  ) ,
        #  StaleHistoryIDs as (
        #     Select distinct SiteID from [oemvm].[dim].[vwAlertAllList]
        #     where AlertID = 12
        # ) ,
        # FinalIDs as (
        #     Select  m.SiteID from StaleHistoryIDs m except select n.SiteID from NiagaraNetworkDownIDs n
        # )
        # select c.Name CustomerName, site.SiteID, site.ShortName SiteName, inst.InstallationID, station.StationID, station.SupervisorID, super.BaseAddressHistory, super.BaseAddressLive
        # from FinalIDs f, oemvm.dim.Customer c, oemvm.dim.Site site
        # join oemvm.dim.Installation inst on inst.SiteID = site.SiteID
        # join oemvm.dim.Station station on station.InstallationID = inst.InstallationID
        # join oemvm.dim.supervisor super on super.SupervisorID = station.SupervisorID
        # where f.SiteID = site.SiteID and site.CustomerID = c.CustomerID
        # and site.SiteID not in (%s)
        #
        # ''' % self.getWhiteList()


        # queryString = '''
        #
        # ;with
        # NiagaraNetworkDownIDs as (
        # select distinct SiteID  from oemvm.dim.vwAlertAllList
        # where ( AlertID = 2 or
        #     (  AlertID = 7 and
        #        AlertName in ('JACE Connection Down', 'NiagaraNetworkDown') )
        #     or AlertID = 14 or  AlertID = 11 )
        #  ),
        #  StaleHistoryIDs as (
        #     Select distinct SiteID from [oemvm].[dim].[vwAlertAllList]
        #     where AlertID = 12
        # ) ,
        # FinalIDs as (
        #     Select  m.SiteID from StaleHistoryIDs m except select n.SiteID from NiagaraNetworkDownIDs n
        # )
        # select c.Name CustomerName, site.SiteID, site.ShortName SiteName, inst.InstallationID, station.StationID, station.SupervisorID, super.BaseAddressHistory, super.BaseAddressLive
        # from FinalIDs f, oemvm.dim.Customer c, oemvm.dim.Site site
        # join oemvm.dim.Installation inst on inst.SiteID = site.SiteID
        # join oemvm.dim.Station station on station.InstallationID = inst.InstallationID
        # join oemvm.dim.supervisor super on super.SupervisorID = station.SupervisorID
        # where f.SiteID = site.SiteID and site.CustomerID = c.CustomerID
        # and site.SiteID not in (%s)
        #
        # ''' % self.getWhiteList()

        queryString = '''

        ;with
        NiagaraNetworkDownIDs as (
        select distinct SiteID  from oemvm.dim.vwAlertAllList
        where ( AlertID = 2 or 
            (  AlertID = 7 and 
               AlertName in ('JACE Connection Down', 'NiagaraNetworkDown') ) 
            or AlertID = 14 or  AlertID = 11 ) 
         ),
         StaleHistoryIDs as (
            Select distinct SiteID from [oemvm].[dim].[vwAlertAllList]
            where AlertID = 12
        ) ,
        FinalIDs as (
            Select  m.SiteID from StaleHistoryIDs m except select n.SiteID from NiagaraNetworkDownIDs n
        )
        select c.Name CustomerName, site.SiteID, site.ShortName SiteName, inst.InstallationID, station.StationID, station.SupervisorID, super.BaseAddressHistory, super.BaseAddressLive
        from FinalIDs f, oemvm.dim.Customer c, oemvm.dim.Site site
        join oemvm.dim.Installation inst on inst.SiteID = site.SiteID
        join oemvm.dim.Station station on station.InstallationID = inst.InstallationID
        join oemvm.dim.supervisor super on super.SupervisorID = station.SupervisorID
        where f.SiteID = site.SiteID and site.CustomerID = c.CustomerID
        and and site.IsIgnoreStaleHistory=0
        '''


        conn = pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True)
        cur = conn.cursor()

        cur.execute( queryString)

        rowCount = 0
        rows = []
        for row in cur:
            rowCount += 1
            rows.append( row )

        conn.close()

        # rows look like {u'CustomerName': u'Amgen', u'SiteName': u'Thousand Oaks }

        return {'rowCount':rowCount, 'rows':rows }


    def getSupervisorList(self):

        queryString = '''
            select distinct s.BaseAddressHistory from oemvmdata.stage.processqueueitem pqi
            join oemvm.dim.supervisor s on pqi.SupervisorID = s.SupervisorID
            where EventInfo is not null
        '''

        conn = pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True)
        cur = conn.cursor()
        cur.execute( queryString )

        rowCount = 0
        rows = []
        for row in cur:
            rowCount += 1
            rows.append( row['BaseAddressHistory'] )

        conn.close()

        # rows look like {u'BaseAddressHistory': u'abcdefg' }

        return rows




    def postTriggerEvent( self, listOfCustomerAndSites) :


        details = json.dumps( listOfCustomerAndSites)

        payload = '''
        {
        "service_key": "%s",
        "incident_key":"%s",
        "event_type": "trigger",
        "description": "Some sites have stale histories",
        "client": "Stale History Warning Tool",
        "details": %s
        }
         ''' % ( self.serviceKey, self.incidentKey, details )

        self.logMsg('Posting trigger event: ' + payload )


        r = requests.post( self.createEventURI, headers=self.headers, data=payload )
        self.logMsg( "post status: " + str( r.status_code ) )
        self.logMsg( "post result: " + r.text )

        if r.status_code != 200 :
            self.logMsg('oops...error: ' + str( r.json() ))


    def postResolveEvent( self, staleDurationStr ):

        payload = '{' + \
        '"service_key":"' + self.serviceKey + '", ' \
        '"incident_key":"' + self.incidentKey + '", ' \
        '"event_type": "resolve",' + \
        '"description": "No sites with stale histories found",' + \
        '"client": "Stale History Warning Tool",' + \
        '"details": { "Problem": "fixed","Duration stale": "' + staleDurationStr + '" }' + \
        '}';

        self.logMsg( "posting resolved event: " + payload)


        r = requests.post( self.createEventURI, data=payload, headers=self.headers )
        self.logMsg( "post status: " + str( r.status_code ) )

        if r.status_code != 200 :
            self.logMsg( "oops...error: " + str( r.json() ) )



    def postToDataDog(self, numOfSitesWithStaleHistory ):

        api.api_key = 'fe1cd13de75c73f4f4de29acd85c4b36'
        api.application_key = 'd0a1be7f8d3d141c8adda765ceb41f90422cbcda'
        metricName = 'foobar.staleHistory.numSites'

        self.logMsg( "posting to DataDog: " + metricName + " = " + str(numOfSitesWithStaleHistory))
        api.metric(metricName, numOfSitesWithStaleHistory)


    def getCustomersAndSites(self, queryResults):
        listOfCustomerAndSites = []

        for row in queryResults :
            val = "%s-%s : %s" % (row['CustomerName'], row['SiteName'], row['BaseAddressHistory'] )
            listOfCustomerAndSites.append(  val );

        return listOfCustomerAndSites


    def loop(self):

        self.logMsg('getting query results')
        queryResults = self.checkDB()

        #print json.dumps( queryResults )

        try:
            listOfCustomerAndSites = self.getCustomersAndSites( queryResults['rows'] )
            count = len( listOfCustomerAndSites )
        except Exception, e:
            print e
            pass


        #post the metric (# of sites w/ stale histories) to dataDog
        self.postToDataDog( count )

        #post to pager duty
        if count > 0 :

            #supervisorList = self.getSupervisorList()
            self.timeOfPostNewEvent = datetime.datetime.now()
            self.postTriggerEvent( listOfCustomerAndSites)

        #post resolve event
        else:
            staleDuration = datetime.datetime.now() - self.timeOfPostNewEvent
            staleDurationStr = self.getTimeDeltaAsString( staleDuration )
            self.postResolveEvent( staleDurationStr )

    def getTimeDeltaAsString(self, td ):
        hours, remainder = divmod( td.seconds, 3600 )
        minutes, seconds = divmod( remainder, 60 )
        td_formatted = '%s:%s:%s' % (hours, minutes, seconds )
        return td_formatted


    def logMsg(self, msg):
        rightNow = datetime.datetime.now()
        ts = rightNow.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        msg = ts + ': ' + msg

        f = open(self.logFilePath, 'a')
        f.write(msg + "\n")
        f.close

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'usage: python batchStaleHistoryWarning.py logfilepath'
        sys.exit(0)

    batchChecker = BatchStaleHistoryWarning(sys.argv[1])

    #print batchChecker.getWhiteList()
    while( True ) :
        try:
            batchChecker.loop()
        except Exception, e:
            print e
            pass
        time.sleep( 60 * 60 * 1 ) #sleep for 1 hours
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