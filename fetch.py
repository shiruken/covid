import pandas as pd

# Load the COVID-19 dataset from USAFacts and reformat
df = pd.read_json("https://usafactsstatic.blob.core.windows.net/public/2020/coronavirus-timeline/allData.json")
df.drop_duplicates(subset=['countyFIPS', 'stateFIPS'], inplace=True)

# Extract most recent confirmed case counts and calculate state totals
df['cases'] = df['confirmed'].apply(lambda x: x[-1])
df['cases'] = df.apply(lambda x: x['cases'] if x['countyFIPS'] else df.groupby('stateAbbr')['cases'].sum()[x['stateAbbr']], axis=1)

# Format FIPS codes for states
df['id'] = df.apply(lambda x: x['countyFIPS'] if x['countyFIPS'] else x['stateFIPS']*1000, axis=1)

# Load the list of state and county FIPS codes
df_counties = pd.read_csv('fips_codes.csv')

# Merge the two DataFrames together
df = pd.merge(df_counties, df, how='left', on='id')
df.fillna(0, inplace=True)
df['cases'] = df['cases'].astype(int)

# Copy data from Washington, DC the 'county' to District of Columbia the 'state'
df.loc[df['id'] == 11000, 'cases'] = df[df['id'] == 11001]['cases'].values[0]

# Export to file
df.to_csv('data.csv', columns=['id', 'name', 'cases'], index=False)