__author__ = 'hal'

import datetime

import pytds


class DSGetRunner():


    def callDSGet2(self):
        

        queryString = '''
                    USE oemvmdata; 
                    declare @blah fact.DataPointsOfInterest, @FromTime datetime, @ToTime datetime, @CacheTime date
                    declare @Results_Orig     fact.DataPointResults
                    declare @Results          fact.DataPointResults
                    insert into @blah (seqnbr, datapointxid, time_aggregatetype, rollup_aggregatetype) 
                    values(1, 'ATT.WB3090.WB3090LP.WB3090LP.OldkW', 'HourlyAvg', 'Sum'), 
                    (2, 'ATT.WB3090.WB3090LP.WB3090LP.ProjkW', 'HourlyAvg', 'Sum'), 
                    (3, 'ATT.WB3090.WB3090LP.WB3090LP.TotalkW', 'HourlyAvg', 'Sum') 
                    set @CacheTime = '2018-07-31' 
                    insert @Results 
                    exec oemvmdata.fact.DataSeriesGet2 @DataPointsOfInterest=@blah, 
                    @TimeRange=null, @TimeInterval='Minute', @FromTime_Local='2018-03-01', @ToTime_Local='2018-04-01', 
                    @IncludeOutOfBounds=0, @IncludeUncommissioned=0, 
                    @CalculatedFromTime = @FromTime, @CalculatedToTime=@ToTime 
                    select * from @Results 
                    '''


        print queryString

        #conn = pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True)
        conn = pytds.connect('e3os-sql.optimumenergy.net', 'oemvmdata', user='hwilkinson', password='GreenDEV90', as_dict=True)
        cur = conn.cursor()
        ttt = cur.execute(queryString)

        #zzz = cur.get_proc_return_status()

        rows_OldkW = []
        rows_ProjkW = []
        rows_TotalkW = []


        aaa = cur.nextset()
        bbb = cur.nextset()
        ccc = cur.nextset()
        data = cur.fetchall()

        conn.close()

        for row in data:

            data = {}

            data['value'] = row['value']
            timestamp = row['time']
            temp = datetime.datetime.strftime( timestamp, '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            data['timestamp'] = temp
            data['tz'] = row['tz'] / 60

            if row['id'] == 1 :
                rows_OldkW.append(data)
            elif row['id'] == 2:
                rows_ProjkW.append(data)
            elif row['id'] == 3 :
                rows_TotalkW.append(data)


        dict = {}
        dict['OldkW'] = rows_OldkW
        dict['ProjkW'] = rows_ProjkW
        dict['TotalkW'] = rows_TotalkW



        # rows look like {u'tz': -300, u'id': 6, u'value': 501.6000061035156, u'time': datetime.datetime(2016, 3, 28, 20, 5, 0, 210000)}

        return dict


if __name__ == '__main__':

    dsGet = DSGetRunner()
    dict = dsGet.callDSGet2()

    numOf_OldkW_Rows = len(dict['OldkW'])
    numOf_ProjkW_Rows = len(dict['ProjkW'])
    numOf_TotalkW_Rows = len(dict['TotalkW'])

    for row in range( 0, numOf_OldkW_Rows ):
        ts = dict['OldkW'][row]['timestamp']
        v = dict['OldkW'][row]['value']
        print( v )






