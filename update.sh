#!/bin/bash

git checkout master && \
git pull && \
env/bin/python fetch.py && \
git add docs/data.csv && \
git commit -m "Updated `date +'%Y-%m-%d %H:%M:%S'`" && \
git push

