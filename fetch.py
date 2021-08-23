import requests
from io import StringIO
import pandas as pd
import numpy as np

# Load county-level data from USAFacts
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}

url = "https://static.usafacts.org/public/data/covid-19/covid_confirmed_usafacts.csv"
r = requests.get(url, headers=headers)
df_cases = pd.read_csv(StringIO(r.text))
df_cases['cases'] = df_cases.iloc[:,-1]
df_cases['new_cases_last_week'] = df_cases.iloc[:,-1] - df_cases.iloc[:,-9]
df_cases['new_cases_2_week_ago'] = df_cases.iloc[:,-16] - df_cases.iloc[:,-24]

url = "https://static.usafacts.org/public/data/covid-19/covid_deaths_usafacts.csv"
r = requests.get(url, headers=headers)
df_deaths = pd.read_csv(StringIO(r.text))
df_deaths['deaths'] = df_deaths.iloc[:,-1]

url = "https://static.usafacts.org/public/data/covid-19/covid_county_population_usafacts.csv"
r = requests.get(url, headers=headers)
df_population = pd.read_csv((StringIO(r.text)))

df = pd.merge(df_cases, df_deaths, how='left', on=['countyFIPS', 'StateFIPS', 'State'])
df = pd.merge(df, df_population, how='left', on=['countyFIPS', 'State'])

# Aggregate county data to calculate state totals
df_state = df.groupby('StateFIPS')[['cases', 'new_cases_last_week', 'new_cases_2_week_ago', 'deaths', 'population']].sum()
df_state['countyFIPS'] = 0
df = pd.merge(df, df_state, how='left', on=['countyFIPS', 'StateFIPS'], suffixes=[None, '_agg'])

idx_state = df['countyFIPS'] == 0
df.loc[idx_state, 'cases'] = df['cases_agg']
df.loc[idx_state, 'new_cases_last_week'] = df['new_cases_last_week_agg']
df.loc[idx_state, 'new_cases_2_week_ago'] = df['new_cases_2_week_ago_agg']
df.loc[idx_state, 'deaths'] = df['deaths_agg']
df.loc[idx_state, 'population'] = df['population_agg']

# Format for export with unified FIPS
df.rename(columns={'countyFIPS': 'FIPS'}, inplace=True)
df['FIPS'] = df.apply(lambda x: x['FIPS'] if x['FIPS'] else x['StateFIPS'], axis=1)
df = df[['FIPS', 'population', 'cases', 'new_cases_last_week', 'new_cases_2_week_ago', 'deaths']]
df = df.astype(int)

df = df[~((df['cases'] == 0) & (df['deaths'] == 0))] # Drop rows with no cases or deaths

df.sort_values(by=['FIPS'], inplace=True)
df.to_csv('docs/data.csv', index=False)
