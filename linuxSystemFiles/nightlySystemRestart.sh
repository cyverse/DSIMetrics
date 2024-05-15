#!/bin/bash

pkill python
cd /home/austinmedina/DataLabMetrtics/budibaseDocker
docker compose down
wait
docker compose up -d
/home/austinmedina/DataLabMetrtics/productionScripts/seriesListener.py &
/home/austinmedina/DataLabMetrtics/zoomApp/zoomOAUTH.py &



