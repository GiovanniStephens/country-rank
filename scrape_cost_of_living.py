# Scrape cost of living by country

"""
To-do:
1. Create some unit tests to ensure that it is working.
I would like to be able to run the tests to know that all the formatting and everything is
still working. It needs to catch if the web page format changes or if there are errors. 

2. Check what countries I am missing from Numbeo and investigate. 

3. Identify what data may be missing. Some countries may be of interest, but I may not be getting info on it.
"""
import scrape_urls
import pandas as pd
import numpy as np

cost_of_living_units = pd.read_csv('Cost of Living Items.csv')
climate_data = pd.read_csv('Climate by Country.csv')

def clean_numbeo_table(numbeo_df):
    """
    Cleans the default Numbeo cost of living table.

    :numbeo_df: pandas dataframe

    :return: pandas dataframe that has been cleaned up.
    """
    # Promote first column to index
    numbeo_df = numbeo_df.set_index(numbeo_df.columns[0])
    # Remove rows where there are nulls in the next column.
    numbeo_df = numbeo_df[~numbeo_df[numbeo_df.columns[0]].isnull()]
    # Replace empty strings with nan
    numbeo_df = numbeo_df.replace(r'^\s*$', np.NaN, regex=True)
    # Replace '?' with NaN 
    numbeo_df = numbeo_df.replace(r'^\?$', np.NaN, regex=True)
    # Split range
    try:
        numbeo_df[['lower', 'upper']] = numbeo_df['Range'].str.split('-', expand = True)
    except:
        numbeo_df['lower'] = np.NaN
        numbeo_df['upper'] = np.NaN
        numbeo_df = numbeo_df.astype(str)
    
    # Remove currency 'NZ$'
    numbeo_df['mode'] = numbeo_df['[ Edit ]'].str[:-4]
    numbeo_df.index.rename('category', inplace = True)
    numbeo_df['lower'] = pd.to_numeric(numbeo_df['lower'].str.replace(',',''), errors='coerce')
    numbeo_df['mode'] = pd.to_numeric(numbeo_df['mode'].str.replace(',',''), errors='coerce')
    numbeo_df['upper'] = pd.to_numeric(numbeo_df['upper'].str.replace(',',''), errors='coerce')
    return numbeo_df


def get_cost_of_living(numbeo_table, simulations = 100000, percentile = 90):
    """
    For all cost categories, get the cost and multiply it by the number of units. 
    I simulate the cost using a triangular distribution if there is a lower and upper bound. 
    If there isn't one though, I simply take the mode.
    """
    vals = np.zeros(simulations)
    for i in range(len(cost_of_living_units) - 1):
        # Will catch an error if the category is not in the table
        try:
            category = cost_of_living_units.iloc[i]['Category']
            units = cost_of_living_units.iloc[i]['Units pw']
            lower = numbeo_table.loc[category]['lower']
            mode = numbeo_table.loc[category]['mode']
            upper = numbeo_table.loc[category]['upper']
            if lower > 0 and upper > 0 and mode > 0:
                vals = np.add(vals, units * np.random.triangular(lower, mode, upper, simulations))
            else:
                vals = np.add(vals, [mode]*simulations)
        except:
            continue
    return np.percentile(vals, percentile)


def check_enough_data(numbeo_df):
    """
    Checks that the number of data points we have is sufficient. 
    I check that I have enough data to be able to use it to estimate cost of living.

    :numbeo_df: pandas dataframe with an '[ Edit ]' column.

    :return: proportion of filled cells as a proportion of number of total categories.
    """
    if type(numbeo_df) == list:
        return 0
    else:
        categories = cost_of_living_units[cost_of_living_units['Units pw'] > 0]['Category']
        intersecting_categories = numbeo_df.index.intersection(categories)
        num_nulls = numbeo_df.loc[intersecting_categories]['[ Edit ]'].isna().sum()
        return (len(intersecting_categories) - num_nulls) / len(categories)


if __name__ == "__main__":
    urls = []
    # Create a url for each country based on the temperature website country names (there may be some differences)
    for country in climate_data['Country']:
        country_str = '+'.join(country.title().split())
        urls.append(f'https://www.numbeo.com/cost-of-living/country_result.jsp?country={country_str}&displayCurrency=NZD')
    soups = scrape_urls.multi_thread_func(scrape_urls.scrape_page, urls)
    tables = [scrape_urls.get_table(soup, 1, 0, -1) for soup in soups]
    cleaned_tables = [clean_numbeo_table(table) for table in tables if type(table) != list]

    cost_of_living_dic = {}
    for country, table in zip(climate_data['Country'], cleaned_tables):
        if check_enough_data(table) > 0.9:
            cost_of_living_dic[country] = get_cost_of_living(table)
    