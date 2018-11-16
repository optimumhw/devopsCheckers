__author__ = 'hal'

import sys
import datetime
import re
import time

import pymssql
import requests
from dogapi import dog_http_api as api

from staleAtomFileCache import StaleAtomFileCache


class StaleAtomFileChecker():

    def __init__( self, logFilePath):
        self.logFilePath = logFilePath
        self.siteCache = StaleAtomFileCache()
        self.testCount = 6


    def checkDB(self):

        queryString = "SELECT TOP 1 AlarmRecordSource, InitialTime, Active " \
            + "FROM [oemvm].[dim].[EventInstances] " \
            + "WHERE AlarmRecordSource = 'OE_J130133_JJ_Vistakon_2:AtomFileOld' AND Active = 1 " \
            + "ORDER BY CreateTime DESC"   

        conn = pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True)
        cur = conn.cursor()
        cur.execute( queryString)

        rowCount = 0
        rows = []
        for row in cur:
            rowCount += 1
            rows.append( row )

        conn.close()

        #{ u'AlarmRecordSource': u'OE_J130133_JJ_Vistakon_2:AtomFileOld', u'InitialTime': u'2015-04-06 04:00:50.000', u'Active':u'1' }
        return {'rowCount':rowCount, 'rows':rows }


    def doPostNewIncidentsToPagerDuty( self, subject, sitesAndDurationDict) :

        for key in sitesAndDurationDict:

            incidentKey = "SAFW-%s" % (key)
            incidentKey = re.sub(' +', '-', incidentKey)

            payload = '{' + \
            '"service_key":"96e5fc31c8db4c23ba9959b83b66c6d5", ' \
            '"incident_key":"' + incidentKey + '", ' \
            '"event_type": "trigger",' \
            '"description": "' + key + ' has stale stale atom file", ' \
            '"client": "Stale Atom File Warning Tool", ' \
            '"details": { "alert type": "stale atom file" } }'

            uri = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
            headers = {'content-type': 'application/json'}

            self.logMessage( 'Posting new incident: ' + payload )

            r = requests.post( uri, headers=headers, data=payload )
            self.logMessage( "post status: " + str( r.status_code ) )

            if r.status_code != 200 :
                self.logMessage( "oops...error: " + str( r.json() ) )




    def doPostResolvesToPagerDuty( self, subject, sitesAndDurationDict ):

        for key in sitesAndDurationDict:

            initialTime = sitesAndDurationDict.get( key )

            incidentKey = "SAFW-%s" % ( key )
            incidentKey = re.sub(' +', '-', incidentKey)

            staleDuration = datetime.datetime.now() - initialTime
            staleDurationStr = self.getTimeDeltaAsString( staleDuration )

            payload = '{"service_key":"96e5fc31c8db4c23ba9959b83b66c6d5", ' \
                  '"incident_key" : "' + incidentKey + '", ' \
                  '"event_type": "resolve",' + \
                  '"description": "' + key + ' has stale atom file",' + \
                  '"client": "Stale Atom File Warning Tool",' + \
                  '"details": { "Problem": "fixed","Duration stale": "' + staleDurationStr + '" }' + \
                  '}';

            uri = "https://events.pagerduty.com/generic/2010-04-15/create_event.json";
            headers = {'content-type': 'application/json'}

            self.logMessage("posting RESOLVED site: " + payload)


            r = requests.post( uri, data=payload, headers=headers )
            self.logMessage( "post status: " + str( r.status_code ) )

            if r.status_code != 200 :
                self.logMessage( "oops...error: " + str( r.json() ) )


    def postToDataDog(self, numOfSitesWithStaleAtomFiles ):

        api.api_key = 'fe1cd13de75c73f4f4de29acd85c4b36'
        api.application_key = 'd0a1be7f8d3d141c8adda765ceb41f90422cbcda'
        self.metricName = 'foobar.staleAtomFile.numSites'

        self.logMessage( "posting to DataDog: " + self.metricName + " = " + str( numOfSitesWithStaleAtomFiles ) )
        api.metric( self.metricName, numOfSitesWithStaleAtomFiles)


    def loop(self):

        queryResults = staleChecker.checkDB()

        #post the metric (# of sites w/ stale histories) to dataDog
        self.postToDataDog( queryResults['rowCount'] )

        #update the cache with new sites
        self.siteCache.updateCache( queryResults['rows'])

        #post the cleared sites to pagerDuty
        self.doPostResolvesToPagerDuty( "resolved problems", self.siteCache.getProblems('cleared'))

        #post the new problems to pagerDuty
        self.doPostNewIncidentsToPagerDuty( "new problems", self.siteCache.getProblems('new'))

        #delete the cleared problems
        self.siteCache.deleteClearedProblemsFromCache()

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
            print 'usage: python StaleAtomFileChecker logfilepath'
            sys.exit(0)

        staleChecker = StaleAtomFileChecker( sys.argv[1])
        while( True ) :
            try:
                staleChecker.loop()
            except Exception, e:
                print e
                pass
            time.sleep( 60 * 60 * 1 ) #sleep for 1 hours
            #time.sleep( 20 ) #sleep for 20 seconds



