import scrape_urls
import numpy as np
import pandas as pd

url = 'https://www.weatherbase.com/weather/countryall.php3'
base_url = 'https://www.weatherbase.com'

def f_to_c(value):
    """
    Converts Fahrenheit to Celsius. 
    """
    return (value - 32)*(5/9)

def in_to_mm(value):
    """
    Converts inches to mm. 
    """
    return value * 25.4

def check_float(potential_float):
    """
    Checks if a string is indeed a float.
    """
    try:
        float(potential_float)
        return True
    except ValueError:
        return False

def get_stats(table):
    """
    Aggregates the climate table data to get the maxes and mins and avgs.
    """
    dic = {}
    if 'Average High Temperature (F)' in table.index:
        dic['max avg max temp'] = f_to_c(table.loc['Average High Temperature (F)'].iloc[1:-2].max())
    if 'Average Low Temperature (F)' in table.index:
        dic['min avg min temp'] = f_to_c(table.loc['Average Low Temperature (F)'].iloc[1:-2].min())
    if 'Average Temperature (F)' in table.index: 
        dic['avg temp'] = f_to_c(table.loc['Average Temperature (F)']['ANNUAL'])
    if 'Average Precipitation (in)' in table.index:
        dic['avg rainfall (mm)'] = in_to_mm(table.loc['Average Precipitation (in)']['ANNUAL'])
    return dic

def get_country_stats(soups):
    """
    For every country, get the stats on its climate.
    """
    dic = {}
    for soup in soups:
        table = scrape_urls.get_table(soup)
        country_name = scrape_urls.find_id_in_html(soup, 'headerfont')[0].text.title()
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