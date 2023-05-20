import pandas as pd

import scrape_urls


def to_pandas_df(rows: list) -> pd.DataFrame:
    """
    Converts a list of HTML rows to a pandas dataframe.

    :rows: list of rows
    :return: pandas dataframe
    """
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
    return pd.DataFrame(table[1:], columns=table[0])


def scrape_index(url: str='https://www.numbeo.com/pollution/rankings_by_country.jsp',
                 columns: tuple = ('Country', 'Pollution')) -> None:
    """
    Scrapes the pollution index from the numbeo website.

    :url: url to scrape.
    :columns: columns to scrape.
    :return: pandas dataframe.
    """
    soup = scrape_urls.scrape_page(url)
    table = soup.find(lambda tag: tag.name == 'table'
                      and tag.has_attr('id') and tag['id'] == "t2")
    rows = table.findAll(lambda tag: tag.name == 'tr')
    table = to_pandas_df(rows)
    table = table[columns]
    table.to_csv(f'{columns[-1].split()[0]} by Country.csv', index=False)


if __name__ == '__main__':
    scrape_index('https://www.numbeo.com/pollution/rankings_by_country.jsp',
                 ['Country', 'Pollution Index'])
    scrape_index('https://www.numbeo.com/health-care/rankings_by_country.jsp',
                 ['Country', 'Health Care Index'])
    scrape_index('https://www.numbeo.com/crime/rankings_by_country.jsp',
                 ['Country', 'Crime Index', 'Safety Index'])
