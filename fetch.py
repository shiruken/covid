import pandas as pd

# Load the COVID-19 dataset from USAFacts and reformat
df = pd.read_json("https://usafactsstatic.blob.core.windows.net/public/2020/coronavirus-timeline/allData.json")
df.drop_duplicates(subset=['countyFIPS', 'stateFIPS'], inplace=True)

# Extract most recent confirmed case counts and calculate state totals
df['cases'] = df['confirmed'].apply(lambda x: x[-1])
df['cases'] = df.apply(lambda x: x['cases'] if x['countyFIPS'] else df.groupby('stateAbbr')['cases'].sum()[x['stateAbbr']], axis=1)

# Format FIPS codes for states
df['id'] = df.apply(lambda x: x['countyFIPS'] if x['countyFIPS'] else x['stateFIPS']*1000, axis=1)

# Drop the row for the Grand Princess Cruise Ship (allocated to California)
df.drop(df[df['county'] == 'Grand Princess Cruise Ship'].index, inplace=True)

# Copy data from Washington, DC the 'county' to District of Columbia the 'state'
df = df.append(df[df['id'] == 11001])
df.iloc[-1, df.columns.get_loc('countyFIPS')] = 0
df.iloc[-1, df.columns.get_loc('id')] = 11000

# Sort the rows and export to file
df.sort_values(by=['id'], inplace=True)
df.to_csv('docs/data.csv', columns=['id', 'cases'], index=False)