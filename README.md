#DevOpsServiceChecks

##Various scripts to check the health of the system:
1. **batchStaleHistoryWarning** - Queries SQL for stale histories. If empty, trending points in E3OS should not show gaps. alerts pagerduty.
1. **batchLiveServiceWarning** - Queries SQL entries in the stale live data table. If empty, plant diagram should be being refreshed. alerts pagerduty.
1. **atomFileStaleChecker** - Checks that the recommendation table is being updated. alerts pager duty.
1. **edisonAPIChecker** - Checks to make sure the edsion API is responding (for Jeremy). alerts pagerduty.
1. **edisonStaleDataChecker** - Checks edison to ensure the timestamps of current values for all AHUs is being updated. alerts pagerduty.
1. **OEdgeSubscriptionPoller** - Creates a live data request for edge, namely for all points on Clark's happy11 station, and polls for live data every 10 seconds. Console output only.


### Prereqs

1. sudo apt-get install python-pip
1. sudo apt-get install freetds-dev
1. sudo apt-get install python-dev
1. sudo pip install pymssql
1. sudo easy_install dogapi

### On Mac
1. brew install freetds
1. pip install pymssql
1. pip install requests




