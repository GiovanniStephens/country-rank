import scrape_urls
import pandas as pd
import numpy as np
import pycountry

cost_of_living_units = pd.read_csv('data/Cost of Living Items.csv')
climate_data = pd.read_csv('data/Climate by Country.csv')


def clean_numbeo_table(numbeo_df: pd.DataFrame) -> pd.DataFrame:
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
        numbeo_df[['lower', 'upper']] = numbeo_df['Range'].str.split('-',
                                                                     expand=True)
    except:
        numbeo_df['lower'] = np.NaN
        numbeo_df['upper'] = np.NaN
        numbeo_df = numbeo_df.astype(str)

    # Remove currency 'NZ$'
    numbeo_df['mode'] = numbeo_df['Edit'].str[:-5]
    numbeo_df.index.rename('category', inplace=True)
    numbeo_df['lower'] = pd.to_numeric(numbeo_df['lower'].str.replace(',', ''),
                                       errors='coerce')
    numbeo_df['mode'] = pd.to_numeric(numbeo_df['mode'].str.replace(',', ''),
                                      errors='coerce')
    numbeo_df['upper'] = pd.to_numeric(numbeo_df['upper'].str.replace(',', ''),
                                       errors='coerce')
    return numbeo_df


def get_cost_of_living(numbeo_table: pd.DataFrame,
                       simulations: int = 20000,
                       percentile: int = 90) -> float:
    """
    For all cost categories, get the cost and multiply
    it by the number of units. I simulate the cost using a
    triangular distribution if there is a lower and upper bound.
    If there isn't one though, I simply take the mode.

    :numbeo_table: pandas dataframe with the cost of living.
    :simulations: number of simulations to run.
    :percentile: percentile to use.
    :return: cost of living in the input country.
    """
    vals = np.zeros(simulations)
    for i in range(len(cost_of_living_units) - 1):
        # Will catch an error if the category is not in the table
        try:
            category = cost_of_living_units.iloc[i]['Category']
            lower_units = cost_of_living_units.iloc[i]['Lower Units pw']
            upper_units = cost_of_living_units.iloc[i]['Upper Units pw']
            lower = numbeo_table.loc[category]['lower']
            mode = numbeo_table.loc[category]['mode']
            upper = numbeo_table.loc[category]['upper']
            if lower > 0 and upper > 0 and mode > 0:
                vals = np.add(vals, np.random.uniform(lower_units,
                                                      upper_units,
                                                      simulations)
                                    * np.random.triangular(lower,
                                                           mode,
                                                           upper,
                                                           simulations))
            else:
                vals = np.add(vals, [mode *
                                     np.random.uniform(lower_units,
                                                       upper_units,
                                                       simulations)]
                                    *simulations)
        except:
            continue
    return np.percentile(vals, percentile)


def check_enough_data(numbeo_df: pd.DataFrame) -> float:
    """
    Checks that the number of data points we
    have is sufficient.
    I check that I have enough data to be able
    to use it to estimate cost of living.

    :numbeo_df: pandas dataframe.
    :return: proportion of filled cells as a proportion of
             number of total categories.
    """
    if type(numbeo_df) == list:
        return 0
    else:
        categories = cost_of_living_units[
                     cost_of_living_units['Upper Units pw'] > 0]['Category']
        intersecting_categories = numbeo_df.index.intersection(categories)
        num_nulls = numbeo_df.loc[intersecting_categories]['Edit'].isna().sum()
        return (len(intersecting_categories) - num_nulls) / len(categories)


def get_numbeo_countries():
    """
    This function returns a list of countries
    that have been scraped from Numbeo.
    The countries get standardized using the pycountry library.
    """
    soup = scrape_urls.scrape_page('https://www.numbeo.com/cost-of-living')
    table = soup.find_all(class_='related_links')
    countries = table[0].find_all('a')
    std_countries = {}
    for i in range(len(countries)):
        try:
            std_countries[countries[i].text] = pycountry.countries.search_fuzzy(
                                               countries[i].text)[0].name
        except:
            pass
    return std_countries


def main():
    urls = []
    # Create a url for each country based on the temperature
    # website country names (there may be some differences).
    countries = get_numbeo_countries()
    for country in countries.keys():
        country_str = '+'.join(country.title().split())
        urls.append(f'https://www.numbeo.com/cost-of-living/country_result.jsp?country={country_str}&displayCurrency=NZD')

    # Scrape the pages
    # soups = scrape_urls.multi_thread_func(scrape_urls.scrape_page, urls)
    soups = [scrape_urls.scrape_page(url) for url in urls]

    # Extract the data tables
    tables = [scrape_urls.get_table(soup, 1, 0, -1) for soup in soups]

    # Clean and format the tables
    cleaned_tables = [clean_numbeo_table(table)
                      if type(table) != list else [] for table in tables]

    # Get cost of living for every country if there is enough data.
    cost_of_living_dic = {}
    for country, table in zip(countries.values(), cleaned_tables):
        if check_enough_data(table) > 0.9:
            cost_of_living_dic[country] = get_cost_of_living(table)
        else:
            cost_of_living_dic[country] = ''

    # Format results table and save
    df = pd.DataFrame.from_dict(cost_of_living_dic, orient='index')
    df.index.rename('Country', inplace=True)
    df.columns = ['Cost of Living pw']
    df.to_csv('data/Cost of Living by Country.csv')


def get_city_cost_of_living(city: str, percentile: int = 90) -> float:
    """
    Get the cost of living for a city.

    :city: city to get the cost of living for.
    :percentile: percentile to use.
    :return: cost of living for the city.
    """
    city = '+'.join(city.title().split())
    url = f'https://www.numbeo.com/cost-of-living/in/{city}?displayCurrency=NZD'
    soup = scrape_urls.scrape_page(url)
    table = scrape_urls.get_table(soup, 1, 0, -1)
    cleaned_table = clean_numbeo_table(table)
    # check if there is enough data
    if check_enough_data(cleaned_table) > 0.9:
        print(str(percentile) + 'th percentile weekly cost of living in ' + city + ': ' +
              str(round(get_cost_of_living(cleaned_table, percentile=percentile), 2)))
    else:
        print('Not enough data to estimate cost of living.')


def get_country_cost_of_living(country: str, percentile: int = 90) -> float:
    """
    Get the cost of living for a country.

    :country: country to get the cost of living for.
    :percentile: percentile to use.
    :return: cost of living for the country.
    """
    country_str = '+'.join(country.title().split())
    url = f'https://www.numbeo.com/cost-of-living/country_result.jsp?country={country_str}&displayCurrency=NZD'
    soup = scrape_urls.scrape_page(url)
    table = scrape_urls.get_table(soup, 1, 0, -1)
    cleaned_table = clean_numbeo_table(table)
    if check_enough_data(cleaned_table) > 0.9:
        print(str(percentile) + 'th percentile weekly cost of living in '
              + country + ': ' +
              str(round(get_cost_of_living(cleaned_table,
                                           percentile=percentile), 2)))
    else:
        print('Not enough data.')
    return get_cost_of_living(cleaned_table, percentile=percentile)


if __name__ == "__main__":
    # get_country_cost_of_living('colombia', 99)
    # get_country_cost_of_living('colombia', 50)
    # get_country_cost_of_living('New zealand', 99)
    # get_country_cost_of_living('New zealand', 50)
    # get_country_cost_of_living('georgia', 99)
    # get_country_cost_of_living('georgia', 50)
    # get_country_cost_of_living('Uruguay', 99)
    # get_country_cost_of_living('Uruguay', 50)
    get_city_cost_of_living('Queenstown', 10)
    get_city_cost_of_living('Tauranga', 10)
    # get_city_cost_of_living('Houston', 50)
    # get_city_cost_of_living('Austin', 50)
    # get_city_cost_of_living('Bogota', 50)
    # get_city_cost_of_living('Medellin', 50)


    # get_city_cost_of_living('Wellington', 90)
    # get_city_cost_of_living('Christchurch', 90)
    # get_city_cost_of_living('Auckland', 90)
    # get_city_cost_of_living('Hamilton', 90)
    # get_city_cost_of_living('Dunedin', 90)
    # get_city_cost_of_living('Bali', 99)
    # get_city_cost_of_living('Bali', 50)
    # get_city_cost_of_living('Yogyakarta', 99)
    # get_city_cost_of_living('Yogyakarta', 50)
    # get_country_cost_of_living('Indonesia', 99)
    # get_country_cost_of_living('Indonesia', 50)
    # get_country_cost_of_living('Thailand', 99)
    # get_country_cost_of_living('Thailand', 50)

    # get_country_cost_of_living('india', 90)
    # get_country_cost_of_living('india', 50)
    # get_country_cost_of_living('Australia', 90)
    # get_country_cost_of_living('Australia', 50)
    # get_country_cost_of_living('Peru', 90)
    # get_country_cost_of_living('Peru', 50)
    # get_country_cost_of_living('Argentina', 90)
    # get_country_cost_of_living('Argentina', 50)
    # get_country_cost_of_living('Ecuador', 90)
    # get_country_cost_of_living('Ecuador', 50)
    # get_country_cost_of_living('Mexico', 90)
    # get_country_cost_of_living('Mexico', 50)
    # get_country_cost_of_living('Spain', 90)
    # get_country_cost_of_living('Spain', 50)
    # get_country_cost_of_living('Portugal', 90)
    # get_country_cost_of_living('Portugal', 50)
    # get_country_cost_of_living('Slovakia', 90)
    # get_country_cost_of_living('Slovakia', 50)
    # get_country_cost_of_living('Pakistan', 90)
    # get_country_cost_of_living('Pakistan', 50)
    # get_country_cost_of_living('Costa Rica', 90)
    # get_country_cost_of_living('Costa Rica', 50)
    # get_country_cost_of_living('Puerto Rico', 90)
    # get_country_cost_of_living('Puerto Rico', 50)
    # get_country_cost_of_living('Iceland', 90)
    # get_country_cost_of_living('Iceland', 50)
