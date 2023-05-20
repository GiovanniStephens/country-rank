from multiprocessing.pool import ThreadPool
from random import choice
from typing import Callable, List, Optional, Union

import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.exceptions import (ConnectionError, HTTPError, ReadTimeout,
                                 RequestException, Timeout, TooManyRedirects,
                                 URLRequired)


def get_table(soup: BeautifulSoup, table_num: int = 2, row_start: int = 1, row_end: int = 5) -> pd.DataFrame:
    """
    Pulls out a table from a beautifulsoup html.

    Format is: Row labels with 'Average' in the name.
    The table returns just the rows 1-4 inclusive.
    This was for the type of tables coming from the climate page.

    :soup: BeautifulSoup object.
    :table_num: The table number to pull out.
    :row_start: The row to start pulling from.
    :row_end: The row to end pulling from.
    :return: a pandas dataframe of the table.
    """
    try:
        table = soup.find_all('table')[table_num]

        # Get headers of table
        t_headers = []
        for th in table.find_all("th"):
            # remove any newlines and extra spaces from left and right
            t_headers.append(th.text.replace('\n', ' ').strip())

        # Get all the rows of table
        table_data = []
        # find all tr's from table's tbody
        for tr in table.find_all("tr"):
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


def find_html_class(soup: BeautifulSoup, class_name: str) -> List[BeautifulSoup]:
    """
    Finds all elements with a given class name.

    :soup: BeautifulSoup object.
    :class_name: The class name to find.
    :return: A list of elements with the given class name.
    """
    return soup.find_all(class_=class_name)


def find_in_html(soup: BeautifulSoup, element: Union[str, list]) -> Optional[BeautifulSoup]:
    """
    Finds an element in a BeautifulSoup object.

    :soup: BeautifulSoup object.
    :element: The element to find.
    :return: The element if found, else None.
    """
    return soup.find_all(element)


def find_id_in_html(soup: BeautifulSoup, id: str) -> Optional[BeautifulSoup]:
    """
    Finds an element with a given id in a BeautifulSoup object.

    :soup: BeautifulSoup object.
    :id: The id to find.
    :return: The element if found, else None.
    """
    return soup.find_all('div', {'id': id})


def proxy_generator() -> dict:
    """
    This function scrapes a list of a free proxies from:

    https://sslproxies.org/

    It then returns a random proxy from the list.
    """
    # Where we get the proxies
    soup = scrape_page("https://sslproxies.org/")

    # Creates the url
    create_url = lambda x: 'http://'+x[0]+':'+x[1]

    # Strip text from soup element
    get_text = lambda x: x.text

    # Get elements from proxy list
    proxy_element1 = map(get_text, soup.findAll('td')[::8])
    proxy_element2 = map(get_text, soup.findAll('td')[1::8])
    proxies = list(zip(proxy_element1, proxy_element2))
    proxy = {'https': choice(list(map(create_url, proxies)))}
    return proxy


def scrape_page(url: str, spoof: bool = False) -> Optional[BeautifulSoup]:
    """
    This function tries to get page information by
    spoofing the header and trying a random proxy.
    If successful, it returns the soup of the page.
    """
    try:
        if spoof:
            proxy = proxy_generator()
            user_agent = UserAgent()
            headers = {'User-Agent': user_agent.random}
            page = requests.get(url, headers=headers, proxies=proxy, timeout=1.5)
            page.raise_for_status()
        else:
            page = requests.get(url)
            page.raise_for_status()
        
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            return soup
        else:
            print(f"There was an error downloading the page {url}.")
    
    except ConnectionError:
        print(f"Could not establish a connection: {url}.")
    except RequestException as e:
        print(f"An error occurred while making the request: {e}.")
    except TooManyRedirects:
        print(f"Too many redirects: {url}.")
    except URLRequired:
        print(f"Please enter a valid URL. {url} is not valid.")
    except ReadTimeout:
        print(f"The server did not return any data within the allotted time: {url}")
    except Timeout:
        print(f"The request timed out: {url}")
    except HTTPError as err:
        print(f"An HTTP error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def multi_thread_func(func: Callable, values: List, threads: int = 126) -> List:
    """
    This function takes a function and a list of values.
    It then runs the function on each value in the list
    using a thread pool.

    :func: The function to run.
    :values: The values to run the function on.
    :threads: The number of threads to use.
    :return: A list of the results of the function.
    """
    listing_soups = []
    with ThreadPool(threads) as pool:
        for result in pool.map(func, values):
            listing_soups.append(result)
    return listing_soups
