import argparse
import json
import os
from urllib.parse import urljoin, urlparse

import pathvalidate
import requests
from bs4 import BeautifulSoup

from parse_tululu_category import get_books_id

URL_BOOK_PAGE = 'http://tululu.org/b{}/'
URL_BOOK_DOWNLOAD = 'http://tululu.org/txt.php'
URL_FANTASY_CATEGORY = 'http://tululu.org/l55/'


def check_for_redirect(response, text=''):
    if response.history:
        raise requests.exceptions.HTTPError(text)


def download_image(url, folder):
    filename = os.path.basename(urlparse(url).path)
    folder_path = os.path.join(folder, 'images')
    path = os.path.join(folder_path, filename)
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder_path, exist_ok=True)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def download_txt(book_id, filename, folder):
    path = os.path.join(folder, 'books', pathvalidate.sanitize_filename(filename))
    response = requests.get(URL_BOOK_DOWNLOAD, params={'id': book_id})
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
        'book_image_url': urljoin(URL_BOOK_PAGE, book_soup.select_one('div.bookimage img').attrs['src']),
        'book_comments': [comment.string for comment in book_soup.select('span.black')],
        'book_genres': [genre.get_text() for genre in book_soup.select('span.d_book a')]
    }
    return book_info


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--start_page', type=int, default=1)
    parse.add_argument('--end_page', type=int, default=0)
    parse.add_argument('--dest_folder', type=str, default='')
    parse.add_argument('--skip_imgs', type=bool, default=False)
    parse.add_argument('--skip_txt', type=bool, default=False)
    parse.add_argument('--json_path', type=str, default='')
    args = parse.parse_args()
    start_page = args.start_page
    end_page = args.end_page if args.end_page else start_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path if args.json_path else os.path.join(dest_folder, 'books_info.json')

    books_info = []

    for book_id in get_books_id(start_page, end_page):
        try:
            response = requests.get(URL_BOOK_PAGE.format(book_id))
            response.raise_for_status()
            check_for_redirect(response)
            page_soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(page_soup)

            books_info.append(
                {
                    'title': book_info['book_name'],
                    'author': book_info['book_author'],
                    'img_src': '' if skip_imgs else download_image(book_info['book_image_url'], folder=dest_folder),
                    'book_path': '' if skip_txt else download_txt(
                        book_id, f'{book_id}. {book_info["book_name"]}.txt', folder=dest_folder
                    ),
                    'comments': book_info['book_comments'],
                    'genres': book_info['book_genres']
                }
            )
            print(URL_BOOK_PAGE.format(book_id))
        except (requests.HTTPError, requests.ConnectionError) as e:
            print(f'\nError downloading the book #{book_id} (URL: {URL_BOOK_PAGE.format(book_id)})')
            print('Details below: ')
            print(e.args, '\n')

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
