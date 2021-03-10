# United States COVID-19 Choropleth

Zoomable choropleth of confirmed COVID-19 cases in the United States. Powered by [D3.js](https://d3js.org/). Hosted on [GitHub Pages](https://pages.github.com/).

https://covid.csullender.com/

## Sources

* Data from [USAFacts](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/) (Previously from [COVID Tracking Project](https://covidtracking.com/))
* TopoJSON from [topojson/us-atlas](https://github.com/topojson/us-atlas)
* Based on [Zoomable Choropleth by Chris Given](https://bl.ocks.org/cmgiven/d39ec773c4f063a463137748097ff52f)
* Legend generated using [d3-legend by Susie Lu](https://d3-legend.susielu.com/)

## About the Data

Data from USAFacts are used for all metrics. The "Hot Spot" metric is the average daily new cases per 100,000 people in the past week and is intended to showcase the current dynamics of COVID-19 infections (inspired by [a New York Times map](https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html)). Regions with fewer than 20 new cases over the last 7 days are not shaded.
