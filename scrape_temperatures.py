from typing import List

import pandas as pd
from bs4 import BeautifulSoup

import scrape_urls

url = 'https://www.weatherbase.com/weather/countryall.php3'
base_url = 'https://www.weatherbase.com'


def f_to_c(value: float) -> float:
    """
    Converts Fahrenheit to Celsius.

    :param value: float of the value to convert.
    :type value: float
    :return: Celisus value.
    :rtype: float
    """
    return (value - 32)*(5/9)


def in_to_mm(value: float) -> float:
    """
    Converts inches to mm.

    :param value: float of the value to convert.
    :type value: float
    :return: mm value.
    :rtype: float
    """
    return value * 25.4


def check_float(potential_float: str) -> bool:
    """
    Checks if a string is indeed a float.

    :param potential_float: string to check.
    :type potential_float: str
    :return: True if the string is a float, False otherwise.
    :rtype: bool
    """
    try:
        float(potential_float)
        return True
    except ValueError:
        return False


def get_stats(table: pd.DataFrame) -> dict:
    """
    Aggregates the climate table data to get the maxes and mins and avgs.

    :param table: pandas dataframe of the table to aggregate.
    :type table: pd.DataFrame
    :return: dictionary of the maxes and mins and avgs.
    :rtype: dict
    """
    dic = {}
    if 'Average High Temperature (F)' in table.index:
        dic['max avg max temp'] = f_to_c(
                                         table.loc['Average High Temperature (F)']
                                         .iloc[1:-2].max())
    if 'Average Low Temperature (F)' in table.index:
        dic['min avg min temp'] = f_to_c(
                                         table.loc['Average Low Temperature (F)']
                                         .iloc[1:-2].min())
    if 'Average Temperature (F)' in table.index:
        dic['avg temp'] = f_to_c(
                                 table.loc['Average Temperature (F)']['ANNUAL'])
    if 'Average Precipitation (in)' in table.index:
        dic['avg rainfall (mm)'] = in_to_mm(
                                            table.loc['Average Precipitation (in)']
                                            ['ANNUAL'])
    return dic


def get_country_stats(soups: List[BeautifulSoup]) -> dict:
    """
    For every country, get the stats on its climate.

    :param soups: list of the soups of the pages.
    :type soups: List[BeautifulSoup]
    :return: dictionary of the stats.
    :rtype: dict
    """
    dic = {}
    for soup in soups:
        table = scrape_urls.get_table(soup)
        country_name = scrape_urls.find_id_in_html(soup,
                                                   'headerfont')[0].text.title()
        dic[country_name] = get_stats(table)
    return dic


def main():
    # Get list of countries
    countries_soup = scrape_urls.scrape_page(url)

    # Get links to each of the country's stats.
    countries = scrape_urls.find_html_class(countries_soup, 'redglow')

    # Create list of urls
    urls = [base_url + countries[i]['href'] for i in range(len(countries))]

    # Scrape all the pages
    soups = scrape_urls.multi_thread_func(scrape_urls.scrape_page, urls)

    # Get stats for each page
    country_stats = pd.DataFrame(get_country_stats(soups))

    # Save the data to a .csv
    country_stats.to_csv('Climate by Country.csv')


if __name__ == '__main__':
    main()
