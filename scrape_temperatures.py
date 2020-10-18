import scrape_urls
import numpy as np
import pandas as pd
from multiprocessing.pool import ThreadPool

def get_table(soup, table_num = 2):
    """
    Pulls out a table from a beautifulsoup html. 

    Format is: Row labels with 'Average' in the name.
    The table returns just the rows 1-4 inclusive. 
    This was for the type of tables coming from the climate page.
    """
    data = {}
    table = soup.find_all('table')[table_num]

    # Get headers of table
    t_headers = []
    for th in table.find_all("th"):
        # remove any newlines and extra spaces from left and right
        t_headers.append(th.text.replace('\n', ' ').strip())
    
    # Get all the rows of table
    table_data = []
    for tr in table.find_all("tr"): # find all tr's from table's tbody
        t_row = {}
        # find all td's in tr and zip it with t_header
        for td, th in zip(tr.find_all("td"), t_headers): 
            val = td.text.replace('\n', '').strip()
            if check_float(val):
                t_row[th] = float(val)
            elif 'Average' in val:
                t_row[th] = val
            else:
                t_row[th] = 0 
        table_data.append(t_row)

    # Put the data for the table with his heading.
    return pd.DataFrame(table_data[1:5]).set_index('')

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
    dic = {}
    for soup in soups:
        table = get_table(soup)
        country_name = scrape_urls.find_id_in_html(soup, 'headerfont')[0].text.capitalize()
        dic[country_name] = get_stats(table)
    return dic

# Multithreading of a given function.
def multi_thread_func(func, values):
    listing_soups = []
    with ThreadPool(126) as pool:
        for result in pool.map(func, values):
            listing_soups.append(result)
    return listing_soups

if __name__ == '__main__':
    url = 'https://www.weatherbase.com/weather/countryall.php3'
    countries_soup = scrape_urls.scrape_page(url)
    countries = scrape_urls.find_html_class(countries_soup, 'redglow')
    urls = ['https://www.weatherbase.com' + countries[i]['href'] for i in range(len(countries))]

    soups = multi_thread_func(scrape_urls.scrape_page, urls)
    country_stats = pd.DataFrame(get_country_stats(soups))
    country_stats.to_csv('Climate by Country.csv')