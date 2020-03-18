#!/bin/bash

git checkout master && \
/home/pi/berryconda3/envs/covid_choropleth/bin/python fetch.py && \
git add data.csv && \
git commit -m "Updated `date +'%Y-%m-%d %H:%M:%S'`" && \
git push && \
git checkout gh-pages && \
git checkout master data.csv && \
git commit -m "Updated `date +'%Y-%m-%d %H:%M:%S'`" && \
git push && \
git checkout master

