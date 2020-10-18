# get list or URLs (done)

# one by one, scrape the table from the links

# as you go, get the average and average max and min temperatures for the countries

import scrape_urls

def get_table(soup):
    """
    Pulls out the table with values labelled 'datac'.
    There are 60 values in 4 rows, and it returns
    a 2D array. 
    """
    values = soup.find_all(class_ = 'datac')
    rows = []
    for i in range(4):
        values = []
        for j in range(15):
            values.append(values[j].text)
        rows.append(values)
    return values

# Create function to get out the max average max 

# Create function to get out the min average min 

# Create function to get out the average 

if __name__ == '__main__':
    url = 'https://www.weatherbase.com/weather/countryall.php3'
    soup = scrape_urls.scrape_page(url)
    countries = scrape_urls.find_html_class(soup, 'redglow')
    urls = ['https://www.weatherbase.com' + countries[i]['href'] for i in range(len(countries))]
    
    print(soup)