# import scrape_temperatures
# import scrape_cost_of_living

from typing import List

import pandas as pd
import pycountry

data = [
    'Climate',
    'Cost of Living',
    'Population Density',
    'Safety',
    'Health',
    'Pollution',
    'Corruption Perception',
    'Freedom'
    ]


def main():
    # scrape_temperatures.main()
    # scrape_cost_of_living.main()
    dfs = import_data()
    dfs[2] = clean_pop_density(dfs[2])
    dfs = standardise_country_names(dfs)
    dfs = promote_to_index(dfs, 'Country')
    joined_data = join_data(dfs[0], dfs[1:])
    joined_data.to_csv('data/All Data by Country.csv')


def standardise_country_names(dfs: List[pd.DataFrame]) -> list:
    """
    Standardisses the country names across all the dataframes.

    :param dfs: list of dataframes.
    :type dfs: List[pd.DataFrame]
    :return: list of dataframes with standardised country names.
    :rtype: List[pd.DataFrame]
    """
    for df in dfs:
        std_countries = []
        for country in df['Country']:
            try:
                if pycountry.countries.search_fuzzy(country)[0].name in ['United States',
                                                                         'United Kingdom',
                                                                         'South Korea']:
                    std_countries.append(
                        pycountry.countries.search_fuzzy(country)[0].name)
                else:
                    std_countries.append(country.title())
            except LookupError:
                std_countries.append(country.title())
        df['Country'] = std_countries
    return dfs


def import_data(suffix: str = ' by Country.csv') -> list:
    """
    Imports all the data into a list of dataframes.

    :param suffix: suffix of the file names.
    :type suffix: str
    :return: list of dataframes.
    :rtype: List[pd.DataFrame]
    """
    dfs = [pd.read_csv('data/'+name+suffix) for name in data]
    return dfs


def join_data(df1: pd.DataFrame, dfs: list) -> pd.DataFrame:
    """
    Joins the dataframes together.

    :param df1: dataframe to be joined.
    :type df1: pd.DataFrame
    :param dfs: list of dataframes to be joined to df1.
    :type dfs: List[pd.DataFrame]
    :return: joined dataframe.
    :rtype: pd.DataFrame
    """
    for df in dfs:
        df1 = df1.join(df)
    return df1


def clean_pop_density(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames the columns in the population density dataframe.

    :param df: dataframe to be cleaned.
    :type df: pd.DataFrame
    :return: cleaned dataframe.
    :rtype: pd.DataFrame
    """
    df.rename(columns={'name': 'Country'}, inplace=True)
    del df['Rank']
    return df


def promote_to_index(dfs: list, col_name: str) -> list:
    """
    Promotes the specified column to the index of the dataframes.

    :param dfs: list of dataframes.
    :type dfs: List[pd.DataFrame]
    :param col_name: name of column to be promoted.
    :type col_name: str
    :return: list of dataframes with the specified
             column promoted to the index.
    :rtype: List[pd.DataFrame]
    """
    return [df.set_index(col_name) for df in dfs]


if __name__ == '__main__':
    main()
