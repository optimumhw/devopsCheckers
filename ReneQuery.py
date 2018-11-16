import pymssql

class ReneQuery():

   def getSomeRows(self):

       queryString = '''
           select distinct s.BaseAddressHistory from oemvmdata.stage.processqueueitem pqi
           join oemvm.dim.supervisor s on pqi.SupervisorID = s.SupervisorID
           where EventInfo is not null
        '''

       conn = pymssql.connect(host='e3os-sql.optimumenergy.net', user='Tominator', password='dT0A@N^V', as_dict=True)
       cur = conn.cursor()
       cur.execute( queryString )

       conn.close()

       return rows

if __name__ == '__main__':

   reneInstance = ReneQuery()
   rows = reneInstance.getSomeRows()
   print rows

