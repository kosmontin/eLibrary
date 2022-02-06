import argparse
import os
from urllib.parse import urljoin, urlparse

import pathvalidate
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

URL_BOOK_PAGE = 'http://tululu.org/b{}/'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_image(url, folder='images'):
    filename = os.path.basename(urlparse(url).path)
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def download_txt(url: tuple, filename, folder='books'):
    book_url, params = url
    response = requests.get(book_url, params=params)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, pathvalidate.sanitize_filename(filename)), 'w') as file:
        file.write(response.text)


def parse_book_page(page_content):
    book_soup = page_content.find('div', {'id': 'content'})
    book_name, book_author = book_soup.find('h1').text.replace('\xa0', '').replace('  ', '').split('::')
    book_info = {
        'book_title': {'book_author': book_author, 'book_name': book_name},
        'book_image_url': urljoin(URL_BOOK_PAGE, book_soup.find('div', class_='bookimage').find('img').attrs['src']),
        'book_comments': [comment.string for comment in book_soup.find_all('span', class_='black')],
        'book_genres': [genre.get_text() for genre in book_soup.find('span', class_='d_book').find_all('a')]
    }
    return book_info


def main():
    url_book_download = 'http://tululu.org/txt.php'

    parse = argparse.ArgumentParser()
    parse.add_argument('start_id', type=int, nargs='?', default=1)
    parse.add_argument('end_id', type=int, nargs='?', default=0)
    args = parse.parse_args()

    for book_id in tqdm(range(args.start_id, args.start_id + 1 if not args.end_id else args.end_id + 1)):
        try:
            response = requests.get(URL_BOOK_PAGE.format(book_id))
            response.raise_for_status()
            check_for_redirect(response)
            page_soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(page_soup)
            download_txt(
                (url_book_download, {'id': book_id}),
                f'{book_id}. {book_info["book_title"]["book_name"]}.txt'
            )
            download_image(book_info['book_image_url'])
        except (requests.HTTPError, requests.ConnectionError) as e:
            print(f'Error downloading the book #{book_id}\n')
            print('Details below: ')
            print(e.args)


if __name__ == '__main__':
    main()
