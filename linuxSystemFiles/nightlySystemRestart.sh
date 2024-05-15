#!/bin/bash

pkill python
cd cd /home/austinmedina/DataLabMetrtics/budibaseDocker
docker compose down
wait
docker compose up
python /home/austinmedina/DataLabMetrtics/productionScripts/seriesListener.py &
python /home/austinmedina/DataLabMetrtics/zoomApp/zoomOAUTH.py &



