#!/bin/bash
#Runs the checkers

nohup python ./batchLiveServiceWarningTool.py ~/oe-test-logs/batchLiveServiceWarningTool.log &
nohup python ./batchStaleHistoryWarning.py ~/oe-test-logs/batchStaleHistoryWarning.log &
nohup python ./edisonApiChecker.py ~/oe-test-logs/edisonApiChecker.log &
nohup python ./edisonStaleDataChecker.py ~/oe-test-logs/edisonStaleDataChecker.log &
nohup python ./atomFileStaleChecker.py ~/oe-test-logs/atomFileStaleChecker.log &



