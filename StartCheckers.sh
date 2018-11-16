#! /bin/sh
#copy this file to /etc/init.d/
#sudo chmod 755 
#sudo update-rc.d StartCheckers.sh defaults

scriptHome="/home/hal/sources/oe-test/oe-test-devopsservicechecks"
logsHome="/home/hal/oe-test-logs"
 
case "$1" in
  start)
    echo "Starting live service checker..."
    python $scriptHome/batchLiveServiceWarningTool.py $logsHome/batchLiveServiceWarningTool.log &
    echo "Starting stale history checker..."
    python $scriptHome/batchStaleHistoryWarning.py $logsHome/batchStaleHistoryWarning.log &
    echo "Starting willlowbrook stale history checker..."
    python $scriptHome/historyCheckWillowbrook.py $logsHome/historyCheckWillowbrook.log &
    echo "Starting edison api checker..."
    python $scriptHome/edisonApiChecker.py $logsHome/edisonApiChecker.log &
    echo "Starting edison stale data checker..."
    python $scriptHome/edisonStaleDataChecker.py $logsHome/edisonStaleDataChecker.log &
    echo "Starting stale atom file checker..."
    python $scriptHome/atomFileStaleChecker.py $logsHome/atomFileStaleChecker.log &
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