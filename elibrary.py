import os

import pathvalidate
import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books'):
    response = requests.get(url)
    response.raise_for_status()
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not response.history:
        with open(os.path.join(folder, pathvalidate.sanitize_filename(filename) + '.txt'), 'wb') as file:
            file.write(response.content)


def main():
    url_book_page = 'http://tululu.org/b{}/'
    url_book_download = 'http://tululu.org/txt.php?id={}'

    for book_id in range(1, 11):
        response = requests.get(url_book_page.format(book_id))
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            print(f'Book #{book_id} not found')
            continue
        page_soup = BeautifulSoup(response.text, 'lxml')
        book_soup = page_soup.find('div', {'id': 'content'})
        book_title = book_soup.find('h1').text.replace('\xa0', '').replace('  ', '').split('::')
        filename = str(book_id) + '. ' + ''.join((book_title[1], ' - ', book_title[0]))
        download_txt(url_book_download.format(book_id), filename)


if __name__ == '__main__':
    main()
