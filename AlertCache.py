__author__ = 'hal'

import datetime

class CacheEntry():

    def __init__(self, cacheEntrySource, initialTime, msg):
        self.cacheEntrySource = cacheEntrySource
        self.initialTime = initialTime
        self.message = msg


class AlertCache():

    def __init__( self):
        self.cache = {}

    def updateCache(self, rowsFromQuery ):

        for key in self.cache :
            self.cache[key].message = 'cleared'

        for row in rowsFromQuery :

            #{ u'AlarmRecordSource': u'OE_J130133_JJ_Vistakon_2:AtomFileOld', u'InitialTime': u'2015-04-06 04:00:50.000', u'Active':u'1' }
            #print row

            key = "%s" % (row['AlarmRecordSource'] )
            si = self.cache.get(key)
            if si is None :
                self.cache[ key ] = SiteInfo( row['AlarmRecordSource'], datetime.datetime.now(), 'new')
            else:
                si.message = 'existing problem'

    def deleteClearedProblemsFromCache(self):

        newCache = {}

        for key in self.cache :
            if self.cache[key].message != 'cleared' :
                newCache[key] = self.cache[key]

        self.cache.clear()

        for key in newCache :
            self.cache[key] = newCache[key]

    def getProblems(self, problemType ):
        dict = {}
        for key in self.cache :
            if self.cache[key].message == problemType :
                dict[ key ] = self.cache[key].initialTime
        return dict









