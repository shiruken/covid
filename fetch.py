import numpy as np
import pandas as pd

# Load and extract the county-level data from USAFacts
df = pd.read_json("https://usafactsstatic.blob.core.windows.net/public/2020/coronavirus-timeline/allData.json")
df.drop_duplicates(subset=['countyFIPS', 'stateFIPS'], inplace=True)
df['cases'] = df['confirmed'].apply(lambda x: x[-1])
df['deaths'] = df['deaths'].apply(lambda x: x[-1])
df.drop(df[df['county'] == 'Grand Princess Cruise Ship'].index, inplace=True)
df.drop(df[df['county'] == 'New York City Unallocated'].index, inplace=True)
df.drop(df[df['countyFIPS'] == 0].index, inplace=True)
df_counties = pd.concat([df['countyFIPS'], df['popul'], df['cases'], df['deaths']], axis=1, keys=['FIPS', 'population', 'cases', 'deaths'])

# Load and extract the state-level data from The COVID Tracking Project
df = pd.read_json("https://covidtracking.com/api/v1/states/current.json")
df.fillna(0, inplace=True)
df_states = pd.concat([df['fips'], df['positive'], df['death']], axis=1, keys=['FIPS', 'cases', 'deaths'])

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

# Calculate the case rate per 100,000 residents
df_output['cases_percapita'] = df_output['cases']/df_output['population']*100000
df_output.replace(np.inf, 0, inplace=True)

# Sort the rows and export to file
df_output.drop(columns='population', inplace=True)
df_output.sort_values(by=['FIPS'], inplace=True)
df_output.to_csv('docs/data.csv', index=False, float_format='%.1f')