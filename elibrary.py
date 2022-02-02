import os
import urllib.parse
from urllib.parse import urljoin, urlparse

import pathvalidate
import requests
from bs4 import BeautifulSoup

URL_BOOK_PAGE = 'http://tululu.org/b{}/'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_image(url, folder='images'):
    filename = os.path.basename(urllib.parse.urlparse(url).path)
    response = requests.get(url)
    response.raise_for_status()
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def download_txt(url, filename, folder='books'):
    response = requests.get(url)
    response.raise_for_status()
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not response.history:
        with open(os.path.join(folder, pathvalidate.sanitize_filename(filename) + '.txt'), 'wb') as file:
            file.write(response.content)


def parse_book_page(page_content):
    book_soup = page_content.find('div', {'id': 'content'})
    book_info = {
        'book_title': [book_soup.find('h1').text.replace('\xa0', '').replace('  ', '').split('::')],
        'book_image_url': urljoin(URL_BOOK_PAGE, book_soup.find('div', class_='bookimage').find('img').attrs['src']),
        'book_comments': [comment.string for comment in book_soup.find_all('span', class_='black')],
        'book_genres': [genre.get_text() for genre in book_soup.find('span', class_='d_book').find_all('a')]
    }
    return book_info


def main():
    url_book_download = 'http://tululu.org/txt.php?id={}'

    for book_id in range(9, 10):
        response = requests.get(URL_BOOK_PAGE.format(book_id))
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            # print(f'Book #{book_id} not found')
            continue
        page_soup = BeautifulSoup(response.text, 'lxml')
        # download_txt(url_book_download.format(book_id), filename)
        # download_image(book_image_url)


if __name__ == '__main__':
    main()
