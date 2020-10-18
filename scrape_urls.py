import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sys
from fake_useragent import UserAgent
from random import choice

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
