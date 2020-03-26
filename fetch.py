import pandas as pd

# Load the COVID-19 dataset from USAFacts and reformat
df = pd.read_json("https://usafactsstatic.blob.core.windows.net/public/2020/coronavirus-timeline/allData.json")
df.drop_duplicates(subset=['countyFIPS', 'stateFIPS'], inplace=True)
df.rename(columns={"countyFIPS": "FIPS"}, inplace=True)

# Extract most recent confirmed case counts and calculate state totals
df['cases'] = df['confirmed'].apply(lambda x: x[-1])
df_states = df.groupby('stateFIPS')['cases'].sum()
df['cases'] = df.apply(lambda x: x['cases'] if x['FIPS'] else df_states[x['stateFIPS']], axis=1)

# Copy state FIPS code to FIPS column
df.loc[df['FIPS'] == 0, 'FIPS'] = df.loc[df['FIPS'] == 0, 'stateFIPS']

# Drop the row for the Grand Princess Cruise Ship (allocated to California)
df.drop(df[df['county'] == 'Grand Princess Cruise Ship'].index, inplace=True)

# Copy data from Washington, DC the 'county' to District of Columbia the 'state'
df = df.append(df[df['FIPS'] == 11001])
df.iloc[-1, df.columns.get_loc('FIPS')] = 11

# Sort the rows and export to file
df.sort_values(by=['FIPS'], inplace=True)
df.to_csv('docs/data.csv', columns=['FIPS', 'cases'], index=False)