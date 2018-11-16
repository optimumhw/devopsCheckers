import sys
import time

class LogWriter():

    def __init__(self, filePath):
        self.logFile = filePath

    def logMessage(self, msg):

        f = open(self.logFile, 'a')
        f.write(msg + "\n")
        f.close

if __name__ == '__main__':

        if len(sys.argv) < 2 :
            print 'usage: TestScript logfilepath'
            sys.exit(0)

        staleChecker = LogWriter( sys.argv[1])
        i=0
        while( True ) :
            try:
                i += 1
                msg = str(i) + " - output"
                staleChecker.logMessage( msg )
            except Exception, e:
                print e
                pass
            #time.sleep( 60 * 60 * 1 ) #sleep for 1 hours
            time.sleep( 5 ) #sleep for 5 seconds
