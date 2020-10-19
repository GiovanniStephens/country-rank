import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sys
from fake_useragent import UserAgent
from random import choice
from multiprocessing.pool import ThreadPool

def get_table(soup, table_num = 2, row_start = 1, row_end = 5):
    """
    Pulls out a table from a beautifulsoup html. 

    Format is: Row labels with 'Average' in the name.
    The table returns just the rows 1-4 inclusive. 
    This was for the type of tables coming from the climate page.
    """
    try:
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
                if val == '---':
                    t_row[th] = '0'
                else:
                    t_row[th] = val
            table_data.append(t_row)

        # Put the data for the table with his heading.
        return pd.DataFrame(table_data[row_start:row_end])
    except:
        return []

def find_html_class(soup, class_name):
    return soup.find_all(class_=class_name)


def find_in_html(soup, element):
    return soup.find_all(element)


def find_id_in_html(soup, id):
    return soup.find_all('div', {'id':id})

#Proxy generator
def proxy_generator():
    """
    This function scrapes a list of a free proxies from:

    https://sslproxies.org/

    It then returns a random proxy from the list. 
    """
    # Where we get the proxies
    soup = scrape_page("https://sslproxies.org/")
    
    # Creates the url
    create_url = lambda x:'http://'+x[0]+':'+x[1]
    
    # Strip text from soup element
    get_text = lambda x:x.text
    
    # Get elements from proxy list
    proxy_element1 = map(get_text, soup.findAll('td')[::8])
    proxy_element2 = map(get_text, soup.findAll('td')[1::8])
    proxies = list(zip(proxy_element1, proxy_element2))
    proxy = {'https': choice(list(map(create_url, proxies)))}
    return proxy

#Scraper
def scrape_page(url, spoof=False):
    """
    This function tries to get page information by spoofing the header and trying a random proxy.
    If successful, it returns the soup of the page. 
    """

    while True:
        try:
            s = requests.Session()
            if spoof:
                proxy = proxy_generator()
                user_agent = UserAgent() 
                headers = {'User-Agent': user_agent.random}
                page = s.get(url,headers=headers, proxies = proxy, timeout=1.5)
            else:
                page = s.get(url)
            if page.status_code == 200:
                # print(f"Page {url} downloaded correctly.")
                soup = BeautifulSoup(page.content, 'html.parser')
                s.close()
                return soup
            else:
                print(f"There was an error downloading the page {url}.")
            s.close()
        except:
            s.close()
            pass

# Multithreading of a given function.
def multi_thread_func(func, values, threads = 126):
    listing_soups = []
    with ThreadPool(threads) as pool:
        for result in pool.map(func, values):
            listing_soups.append(result)
    return listing_soups