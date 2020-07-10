import numpy as np
import pandas as pd

# Load and extract the county-level data from USAFacts
df_cases = pd.read_csv("https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv")
df_deaths = pd.read_csv("https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv")
df_population = pd.read_csv("https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_county_population_usafacts.csv")

df_cases['cases'] = df_cases.iloc[:,-1]
new_cases_1_wk = df_cases.iloc[:,-9:-1].diff(axis=1).iloc[:,1:]
new_cases_2_wk = df_cases.iloc[:,-16:-8].diff(axis=1).iloc[:,1:]
df_cases['hot'] = new_cases_1_wk.mean(axis=1) / new_cases_2_wk.mean(axis=1)
df_cases.loc[new_cases_1_wk.sum(axis=1) < 20, 'hot'] = -1

df_deaths['deaths'] = df_deaths.iloc[:,-1]

df = pd.merge(df_cases, df_deaths, how='left', on=['countyFIPS', 'stateFIPS', 'State'])
df = pd.merge(df, df_population, how='left', on=['countyFIPS', 'State'])
df.drop(df[df['County Name_x'] == 'Grand Princess Cruise Ship'].index, inplace=True)
df.drop(df[df['County Name_x'] == 'New York City Unallocated/Probable'].index, inplace=True)
df.drop(df[df['countyFIPS'] == 0].index, inplace=True)
df_counties = pd.concat([df['countyFIPS'], df['population'], df['cases'], df['hot'], df['deaths']], 
                        axis=1, keys=['FIPS', 'population', 'cases', 'hot', 'deaths'])
df_counties['population'] = df_counties['population'].astype(int)

# Load and extract the state-level data from The COVID Tracking Project
df = pd.read_json("https://covidtracking.com/api/v1/states/daily.json")
df.fillna(0, inplace=True)
df = df.pivot(index='fips', columns='date', values=['positive', 'death', 'positiveIncrease']).reset_index()
df['cases'] = df['positive'].iloc[:,-1]
new_cases_1_wk = df['positiveIncrease'].iloc[:,-8:-1]
new_cases_2_wk = df['positiveIncrease'].iloc[:,-15:-8]
df['hot'] = new_cases_1_wk.mean(axis=1) / new_cases_2_wk.mean(axis=1)
df.loc[new_cases_1_wk.sum(axis=1) < 20, 'hot'] = -1
df['deaths'] = df['death'].iloc[:,-1]

df_states = pd.concat([df['fips'], df['cases'], df['hot'], df['deaths']], axis=1, keys=['FIPS', 'cases', 'hot', 'deaths'])
df_states = df_states.convert_dtypes()

# Calculate the state populations using the county-level data
df_states['population'] = df_states['FIPS'].apply(lambda x: df_counties[df_counties['FIPS'].between(x*1000, (x + 1)*1000, inclusive=False)]['population'].sum())

# Combine the state and county data
df_output = df_counties.append(df_states)

# Copy the data from Washington, DC the "state" to Washington, DC the "county"
# Assumes that COVID Tracking Project is more up-to-date than USAFacts
df_output.loc[df_output['FIPS'] == 11001, 'cases'] = df_output[df_output['FIPS'] == 11]['cases'].values[0]
df_output.loc[df_output['FIPS'] == 11001, 'deaths'] = df_output[df_output['FIPS'] == 11]['deaths'].values[0]

# Drop all rows where no cases or deaths were reported
df_output = df_output[~((df_output['cases'] == 0) & (df_output['deaths'] == 0))]

# Sort the rows and export to file
df_output.sort_values(by=['FIPS'], inplace=True)
df_output.to_csv('docs/data.csv', index=False, float_format='%.3f')