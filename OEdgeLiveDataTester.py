__author__ = 'hal'


'''
OEdgeLiveDataTester:
- Logs into OEDev as test@optimumenergyco.com,
- Creates a live data request for all points associated with Clark's happy11 station,
- And then queries for live data every 10 seconds
'''
import datetime
import json
import time

import requests


class OEdgeLiveDataTester():

    def __init__( self, host, username, password, stationSid ):

        self.VERSION = '2016.06'
        self.USERNAME = username
        self.PASSWORD = password
        self.stationSid = stationSid

        self.OEURL = 'https://' + host + '/api/' + self.VERSION
        self.token = ""
        self.headers = {'content-type': 'application/json'}


        self.pointsList = ["CDWP2SPD","CDWRT","CH1CHWRT","CH3CHWDP","CDWPSPD","CH1S","CH2DMD","CH1CDWFLO","CH3CHWSTSP","CH1CHWVLV","EDGEMODE","CH3COMDISCHT","CDWP3S","CH3COM1F","CDWST","CDWP1S","PCHWP2S","CH2AVAIL","PCHWP3Failed","CHWSTSP","CT1kW","OEWATCHDOG","CH1CDT","PCHWP2SPD","CT2Failed","CH1CHWFLO","CH2SS","PCHWP1SPD","CH3COM1SPD","CT1SPD","PCHWP3S","CH1CHWSTSP","CH2EVT","CH3CDP","CHWRP","CH3ALARM","CH3CHWRT","CH1COM1kW","CH2S","CDWBPV","CH1SURGE","CH2kW","CT2kW","PCHWP1kW","CH3COM1S","CH3CDWFLO","CH1COM1SPD","CH3EVP","CH1EVT","CT2S","CH2CDWVLV","CDWP2SPDNotOptimized","CH2CHWSTSP","CH2COMDISCHT","CH3CDWDP","CH3COM1kW","CDWP2S","CT1Failed","CDWP1SPD","CH1F","CH1ALARM","CH3CDT","CH3kW","CH3EVT","CH2CHWRT","CH1COM1F","CH1COM1S","CH1CDWVLV","CT1EVLV","CHWDP","PCHWP3kW","CDWP1SS","CH2EVP","CDWP3SS","CH2CDWFLO","CH1DMD","CH2CHWVLV","CH3COM1IGV","CDWSTSP","CH2F","CH1kW","CHWFLO","CHWST","CDWFLO","CHWBPV","CH1CHWSTSPNotOptimized","CH2COM1IGV","CH3DMD","CH1COMDISCHT","CH3F","CH3CHWST","CT1S","CH1SS","PCHWP1SS","CHWFLO2","CT1LVLV","CH2ALARM","CH2COM1SPD","CH3CHWVLV","CDWP1SPDNotOptimized","CH3AVAIL","CH3SS","CHWRT","CH1CDWST","PCHWP3SS","CDWP2kW","CH2CHWSTSPNotOptimized","CH1AVAIL","CH2CDWRT","CH2CHWFLO","PCHWP2kW","CH2COM1S","CH2CDWDP","CDWP2SS","PCHWP3SPDNotOptimized","PCHWP1SPDNotOptimized","PCHWP1S","CH2CDWST","ACHWDPSP","CH3CHWSTSPNotOptimized","PCHWP1Failed","CH3S","CDWP3SPD","CTFANSPDMAX","PCHWP2Failed","CT2SS","CH1COM1IGV","CH3CDWST","CH1FLA","CHWDPSP","CH3CDWVLV","CH3SURGE","PCHWP2SS","CHWSP","CH1CHWST","EDGEREADY","CH2SURGE","CT2SPD","PCHWP2SPDNotOptimized","CH3CHWFLO","CH1CDWDP","CH2COM1F","CT2EVLV","CT2LVLV","CH1CHWDP","BASWATCHDOG","CH2COM1kW","CH1EVP","CDWP1Failed","CT1SS","CT2SPDNotOptimized","CDWP3Failed","CH3FLA","CH2CHWST","CH3CDWRT","PCHWP3SPD","CH2CDT","CH2CHWDP","OAT","CDWP1kW","CDWP3SPDNotOptimized","COMLOSSBAS","CLGMODE","CT1SPDNotOptimized","CH1CDP","OAH","CDWP3kW","CDWP2Failed","CH2CDP","CH2FLA","CH1CDWRT"]


    def getToken(self ):

        url = self.OEURL + '/auth/oauth/token'

        headers = {}
        headers['content-type'] = 'application/json'

        dict = {}
        dict['scope'] = 'read+write'
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

    def getCustomers(self):
        url = self.OEURL + '/customers'

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to query for customers'


    def getCreateSubscriptionPayload(self):

        todaysDate = datetime.datetime.now()
        timestamp = datetime.datetime.strftime( todaysDate, '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        points = {}
        points[ self.stationSid ] = self.pointsList

        dict = {}
        dict['timestamp'] = timestamp
        dict['points'] = points

        return dict


    def createSubscription(self):

        url = self.OEURL + '/live'

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Accept'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token

        payload = json.dumps( self.getCreateSubscriptionPayload() )
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to create subscription'

    def queryForLiveData(self, subscriptionId ):

        url = self.OEURL + '/live?subscriptionId=' + subscriptionId

        headers = {}
        headers['content-type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + self.token
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r.status_code, json.loads(r.text)

        return r.status_code, 'failed to query for live data'


    def getCustomerTemplate(self, customerName, extSfId):

        address = {}

        address['street'] = '411 First Avenue'
        address['city'] = 'Seattle'
        address['state'] = 'Washington'
        address['country'] = 'USA'
        address['zipcode'] = '92111'

        customer = {}
        customer['name'] = customerName
        customer['extSfId'] = extSfId
        customer['address']


if __name__ == '__main__':
        host = 'opticx.oedev.us'
        username = 'test@optimumenergyco.com'
        password = 'password'
        stationSid = 'c:matthysent.s:happy11c-edge.st:1'
        testCustomerName = 'Hals Customer'

        api = OEdgeLiveDataTester( host, username, password, stationSid )

        # 1.) Authenticate
        status, oauthToken = api.getToken()
        if status != 200:
            print status, 'failed to get token'
            exit()


        # 2.) Locate customer
        status, customerList = api.getCustomers()
        customers = customerList['customers']

        foundIt = false
        for customer in customerList['customers']:
            if customer['name'] == testCustomerName:
                foundIt = True

        if not foundIt:
            api.createCustomer



        # 2.) Create subscription
        status, subcriptionResponse = api.createSubscription()
        if status != 200:
            print status, 'failed to get sites', status
            exit()

        subscriptionId = subcriptionResponse['subscriptionId']

        while( True ) :
            try:
                status, liveDataResp = api.queryForLiveData( subscriptionId )
                if status != 200:
                    print status, 'failed to query for live data'
                else:

                    todaysDate = datetime.datetime.now()
                    timestamp = datetime.datetime.strftime( todaysDate, '%Y-%m-%d %H:%M:%S')

                    pointName = liveDataResp['datapoints'][0]['name']
                    pointValue = liveDataResp['datapoints'][0]['value']
                    print '%s   %s : %.3f' % (timestamp, pointName, pointValue)
            except Exception, e:
                print e
                pass
            time.sleep( 10 ) #sleep for 10 seconds




