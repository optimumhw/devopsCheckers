#! /bin/sh
#copy this file to /etc/init.d/
#sudo chmod 755 
#sudo update-rc.d StartCheckers.sh defaults

scriptHome=$OE_TEST_HOME/devopsCheckers
 
case "$1" in
  start)
    echo "Starting live service checker..."
    python $scriptHome/batchLiveServiceWarningTool.py $CHECKER_LOGS_HOME/batchLiveServiceWarningTool.log &
    echo "Starting stale history checker..."
    python $scriptHome/batchStaleHistoryWarning.py $CHECKER_LOGS_HOME/batchStaleHistoryWarning.log &
    echo "Starting willlowbrook stale history checker..."
    python $scriptHome/historyCheckWillowbrook.py $CHECKER_LOGS_HOME/historyCheckWillowbrook.log &
    echo "Starting edison api checker..."
    python $scriptHome/edisonApiChecker.py $CHECKER_LOGS_HOME/edisonApiChecker.log &
    echo "Starting edison stale data checker..."
    python $scriptHome/edisonStaleDataChecker.py $CHECKER_LOGS_HOME/edisonStaleDataChecker.log &
    echo "Starting stale atom file checker..."
    python $scriptHome/atomFileStaleChecker.py $CHECKER_LOGS_HOME/atomFileStaleChecker.log &
    ;;
  stop)
    echo "Killing checkers!"
    killall python
    ;;
  *)
    echo "Usage: /etc/init.d/StartCheckers.sh{start|stop}"
    exit 1
    ;;
esac
 
exit 0