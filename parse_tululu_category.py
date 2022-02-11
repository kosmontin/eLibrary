import requests
from bs4 import BeautifulSoup

FANTASY_SECTION_URL = 'http://tululu.org/l55/'

SITE_URL = 'http://tululu.org'


def get_books_id(start_page, end_page, url=FANTASY_SECTION_URL):
    books_id = []
    num_page = start_page
    while num_page <= end_page:
        response = requests.get(f'{url}{num_page}/')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books_soup = soup.select('div#content table.d_book')
        for book in books_soup:
            books_id.append(book.select_one('a').attrs['href'][2:-1])
        num_page += 1
    return books_id
