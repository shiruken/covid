import numpy as np
import pandas as pd

# Load and extract the county-level data from USAFacts
df_cases = pd.read_csv("https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv")
df_deaths = pd.read_csv("https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv")
df_population = pd.read_csv("https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_county_population_usafacts.csv")

df_cases['cases'] = df_cases.iloc[:,-1]
df_cases['new_cases_last_week'] = df_cases.iloc[:,-1] - df_cases.iloc[:,-9]
df_cases['new_cases_2_week_ago'] = df_cases.iloc[:,-16] - df_cases.iloc[:,-24]
df_deaths['deaths'] = df_deaths.iloc[:,-1]

df = pd.merge(df_cases, df_deaths, how='left', on=['countyFIPS', 'stateFIPS', 'State'])
df = pd.merge(df, df_population, how='left', on=['countyFIPS', 'State'])
df.drop(df[df['County Name_x'] == 'Grand Princess Cruise Ship'].index, inplace=True)
df.drop(df[df['County Name_x'] == 'New York City Unallocated/Probable'].index, inplace=True)
df.drop(df[df['countyFIPS'] == 0].index, inplace=True)
df_counties = pd.concat([df['countyFIPS'], df['population'], df['cases'], df['new_cases_last_week'], df['new_cases_2_week_ago'], df['deaths']], 
                        axis=1, keys=['FIPS', 'population', 'cases', 'new_cases_last_week', 'new_cases_2_week_ago', 'deaths'])
df_counties['population'] = df_counties['population'].astype(int)

# Load and extract the state-level data from The COVID Tracking Project
df = pd.read_json("https://covidtracking.com/api/v1/states/daily.json")
df.fillna(0, inplace=True)
df = df.pivot(index='fips', columns='date', values=['positive', 'death']).reset_index()
df['cases'] = df['positive'].iloc[:,-1]
df['new_cases_last_week'] = df['positive'].iloc[:,-1] - df['positive'].iloc[:,-8]
df['new_cases_2_week_ago'] = df['positive'].iloc[:,-15] - df['positive'].iloc[:,-22]
df['deaths'] = df['death'].iloc[:,-1]

df_states = pd.concat([df['fips'], df['cases'], df['new_cases_last_week'], df['new_cases_2_week_ago'], df['deaths']], 
                      axis=1, keys=['FIPS', 'cases', 'new_cases_last_week', 'new_cases_2_week_ago', 'deaths'])
df_states = df_states.astype(int)

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
df_output.to_csv('docs/data.csv', index=False, float_format='%d')