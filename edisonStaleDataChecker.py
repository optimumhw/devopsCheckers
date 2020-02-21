__author__ = 'hal'

'''

EdisonStaleDataChecker - Runs once per hour and posts data to pager duty if:

The optimizaionStatus point has not been updated within three hours.
The check is against EVERY ahu belonging to:

c:jj.s:lajolla
c:jj.s:sanlorenzo
c:lifebridge.s:sinai

'''

import sys
import datetime
import json
import os
import time

import pymssql
import requests

from AlertCache import AlertCache


class EdisonStaleDataChecker():

    def __init__( self, logFilePath, host, username, password ):

        self.alertCache = AlertCache()

        self.logFilePath = logFilePath
        self.HOST = host
        self.VERSION = '2015.04'
        self.AUTH_VERSION = '2015.10'
        self.USERNAME = username
        self.PASSWORD = password

        self.OEURL = self.HOST + '/api/' + self.VERSION
        self.AUTHURL = self.HOST + '/api/' + self.AUTH_VERSION

        self.token = ""

        self.incidentKey = "EdisonStaleDataWarning"
        self.serviceKey = "96e5fc31c8db4c23ba9959b83b66c6d5"
        self.createEventURI = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        self.headers = {'content-type': 'application/json'}


    def getToken(self ):

        url = self.AUTHURL + '/oauth/token'

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


    def getPointMetadata(self, sid, pointName):

        url = self.OEURL + '/' + sid + '/datapoint_metadata?datapoints=' + pointName

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to get point metadata'


    def getSpWho2Info(self):

        with pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True) as conn:
            with conn.cursor() as cur:
                cur.callproc('sp_who2')
                rows = []
                for row in cur:
                    jsonRowString = json.dumps(row)
                    jsonRow = json.loads( jsonRowString )
                    rows.append( jsonRow )
        return rows


    def loop(self, sidsAndPoints):

        status, msg = self.getToken()

        if status != 200:
            payload = 'http status code: ' + str(status) + ' - ' + msg
            self.doPostNewIncidentsToPagerDuty( payload )
            return

        details = {}


        for (sid, dataPoint) in sidsAndPoints:

            key = sid + '-' + dataPoint

            status, dict = self.getPointMetadata( sid, dataPoint )

            if status != 200 :
                details[key] = dict
            else:
                try:
                    stamp = dict['points'][0]['currentTimestamp']
                    lastUpdated = datetime.datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                    rightNow = datetime.datetime.utcnow()
                    lapse = rightNow - lastUpdated
                    numSeconds = lapse.total_seconds()
                    if numSeconds > 60 * 60 * 3 :
                        msg = 'lastUpdated = ' + self.getTimeDeltaAsString(lapse) + ' (days ago)'
                        details[key] = msg

                except Exception, e:
                    msg =  'could not calculate time lapse'
                    details[key]=msg
                    pass


        if len( details ) > 0 :

            sp_who2_output_rows = []
            try:
                #get sp_who2 info
                #sp_who2_output_rows = self.getSpWho2Info()
                pass
            except Exception, e:
                self.logMessage('could not get sp_who2 results')
                self.logMessage(e)
                pass

            self.doPostNewIncidentsToPagerDuty( details, sp_who2_output_rows )
            return

        else:
            todaysDate = datetime.datetime.now()
            someTimeStamp = datetime.datetime.strftime( todaysDate, '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            self.logMessage( someTimeStamp + " and all is well" )

    def getTimeDeltaAsString(self, td ):
        hours, remainder = divmod( td.seconds, 3600 )
        minutes, seconds = divmod( remainder, 60 )
        td_formatted = '%s:%s:%s' % (hours, minutes, seconds )
        return td_formatted


    #===============================

    def doPostNewIncidentsToPagerDuty( self, details, sp_who2_output_rows ) :

        msg2 = '"sp_who2_output":' + json.dumps(sp_who2_output_rows)

        payload = '{' + \
        '"service_key":"3fd18d12de5b49a2b2e8cfbcb7b9c6e4", ' \
        '"incident_key":"' + self.incidentKey + '", ' \
        '"event_type": "trigger",' \
        '"description": "Some sites have stale Edison data", ' \
        '"client": "Edison Stale Data Checker", ' \
        '"details":' + json.dumps(details) + ',' + msg2 + '}'

        uri = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
        headers = {'content-type': 'application/json'}

        self.logMessage( 'Posting new incident: ' + payload )

        '''
        r = requests.post( uri, headers=headers, data=payload )
        self.logMessage( "post status: " + str( r.status_code ) )

        if r.status_code != 200:
            self.logMessage( "oops...error: " + str( r.json() ) )
        '''

    def logMessage(self, msg):

        f = open(self.logFilePath, 'a')
        f.write(msg + "\n")
        f.close

if __name__ == '__main__':

        if len(sys.argv) < 2 :
            print 'usage: python edisonStaleDataChecker.py logfilepath'
            sys.exit(0)

        username = os.environ['TESTUSER'].strip()
        password =  os.environ['TESTUSERPASSWORD'].strip()

        host = 'https://opticx.optimumenergyco.com'

        edisonStaleDataChecker = EdisonStaleDataChecker( sys.argv[1], host, username, password )
        while( True ) :
            try:
                sidsAndPoints = []

                #LaJolla
                lajollaAHUs = [1,2,4,5,6,7,8,11,12,13,14,15,16]
                for ahu in lajollaAHUs :
                    sidsAndPoints.append( ('c:jj.s:lajolla.e:ahu' + str(ahu), 'OptimizationStatus'))

                #San Lorenzo
                slAHUs = [409,308,310,313,309,410,301]
                for ahu in slAHUs :
                    sidsAndPoints.append( ('c:jj.s:sanlorenzo.e:ahu' + str(ahu), 'OptimizationStatus'))

                #LifeBridge
                for i in range(1,23,1):
                    sidsAndPoints.append( ('c:lifebridge.s:sinai.e:ahu' + str(i), 'OptimizationStatus'))

                edisonStaleDataChecker.loop( sidsAndPoints )
            except Exception, e:
                print e
                pass
            time.sleep( 60 * 60 * 1 ) #sleep for 1 hours
            #time.sleep( 20 ) #sleep for 20 seconds


