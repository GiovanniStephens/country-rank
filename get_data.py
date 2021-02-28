# Orchestrates getting all the data

import scrape_temperatures
import scrape_cost_of_living

import pandas as pd
import pycountry

data = [
    'Climate',
    'Cost of Living',
    'Population Density'
    ]

def main():
    # scrape_temperatures.main()
    # scrape_cost_of_living.main()
    dfs = import_data()
    dfs[2] = clean_pop_density(dfs[2])
    dfs = standardise_country_names(dfs)
    dfs = promote_to_index(dfs, 'Country')
    joined_data = join_data(dfs[0], dfs[1:])
    joined_data.to_csv('All Data by Country.csv')

def standardise_country_names(dfs):
    for df in dfs:
        std_countries = []
        for country in df['Country']:
            try:
                std_countries.append(pycountry.countries.search_fuzzy(country)[0].name)
                print(f'{country} --> {pycountry.countries.search_fuzzy(country)[0].name}')
            except:
                std_countries.append(country)
        df['Country'] = std_countries
    return dfs

def import_data(suffix = ' by Country.csv'):
    dfs = [pd.read_csv(name+suffix) for name in data]
    return dfs

def join_data(df1, dfs):
    for df in dfs:
        df1 = df1.join(df)
    return df1

def clean_pop_density(df):
    df.rename(columns={'name':'Country'}, inplace=True)
    del df['Rank']
    return df

def promote_to_index(dfs, col_name):
    return [df.set_index(col_name) for df in dfs]

if __name__ == '__main__':
    main()
