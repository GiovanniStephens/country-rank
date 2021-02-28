from bs4 import BeautifulSoup  
import scrape_urls
import pandas as pd
url = 'https://www.numbeo.com/crime/rankings_by_country.jsp'

def to_pandas_df(rows):
    table = []
    headers = []
    for element in rows[0].find_all('th'):
        headers.append(element.text)
    table.append(headers)

    for row in rows[1:]:
        row_elements = []
        for cell in row.find_all('td'):
            row_elements.append(cell.text)
        table.append(row_elements)
    return pd.DataFrame(table[1:],columns=table[0])

def main():
    soup = scrape_urls.scrape_page(url)
    table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="t2")
    rows = table.findAll(lambda tag: tag.name=='tr')
    table = to_pandas_df(rows)
    table = table[['Country', 'Crime Index', 'Safety Index']]
    table.to_csv('Safety by Country.csv', index=False)

if __name__ == '__main__':
    main()
