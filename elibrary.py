import argparse
import json
import os
from urllib.parse import urljoin, urlparse

import pathvalidate
import requests
from bs4 import BeautifulSoup

from parse_tululu_category import get_books_id

BOOK_PAGE_URL = 'http://tululu.org/b{}/'
DOWNLOAD_BOOK_URL = 'http://tululu.org/txt.php'
FANTASY_SECTION_URL = 'http://tululu.org/l55/'


def check_for_redirect(response, text=''):
    if response.history:
        raise requests.exceptions.HTTPError(text)


def download_image(url, folder):
    filename = os.path.basename(urlparse(url).path)
    folder_path = os.path.join(folder, 'images')
    path = os.path.join(folder_path, filename).replace('\\', '/')
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder_path, exist_ok=True)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def download_txt(book_id, filename, folder):
    path = os.path.join(folder, 'books', pathvalidate.sanitize_filename(filename)).replace('\\', '/')
    response = requests.get(DOWNLOAD_BOOK_URL, params={'id': book_id})
    response.raise_for_status()
    check_for_redirect(response, 'Trying to download txt file')
    os.makedirs(os.path.join(folder, 'books'), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return path


def parse_book_page(page_content):
    book_soup = page_content.select_one('div#content')
    book_name, book_author = book_soup.select_one('h1').text.replace('\xa0', '').replace('  ', '').split('::')
    book_info = {
        'book_author': book_author,
        'book_name': book_name,
        'book_image_url': urljoin(BOOK_PAGE_URL, book_soup.select_one('div.bookimage img').attrs['src']),
        'book_comments': [comment.string for comment in book_soup.select('span.black')],
        'book_genres': [genre.get_text() for genre in book_soup.select('span.d_book a')]
    }
    return book_info


def get_lastpage_num(url=FANTASY_SECTION_URL):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    num_pages = soup.select('p.center a')
    num_page = int(num_pages[-1].text) if num_pages else None
    return num_page


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--start_page', type=int, default=1)
    parse.add_argument('--end_page', type=int, default=get_lastpage_num())
    parse.add_argument('--dest_folder', type=str, default='')
    parse.add_argument('--skip_imgs', action='store_true')
    parse.add_argument('--skip_txt', action='store_true')
    parse.add_argument('--json_path')
    args = parse.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path if args.json_path else os.path.join(dest_folder, 'books_info.json')

    books_info = []

    for book_id in get_books_id(start_page, end_page):
        try:
            response = requests.get(BOOK_PAGE_URL.format(book_id))
            response.raise_for_status()
            check_for_redirect(response)
            page_soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(page_soup)
            book_info['img_src'] = '' if skip_imgs else download_image(book_info['book_image_url'], folder=dest_folder)
            book_info['book_path'] = '' if skip_txt else download_txt(
                book_id,
                f'{book_id}. {book_info["book_name"]}.txt',
                folder=dest_folder
            )
            books_info.append(book_info)
        except (requests.HTTPError, requests.ConnectionError) as e:
            print(f'Error downloading the book #{book_id} (URL: {BOOK_PAGE_URL.format(book_id)})')
            print('Details below: ')
            print(e.args)

    if os.path.dirname(json_path):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
