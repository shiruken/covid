#!/bin/bash

git checkout master && \
git pull && \
/home/pi/berryconda3/envs/covid_choropleth/bin/python fetch.py && \
git add docs/data.csv && \
git commit -m "Updated `date +'%Y-%m-%d %H:%M:%S'`" && \
git push

