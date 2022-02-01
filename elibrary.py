import os

import requests


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def main():
    url = 'http://tululu.org/txt.php'

    if not os.path.exists('books'):
        os.makedirs('books')

    for book_id in range(1, 11):
        response = requests.get(url, params={'id': book_id})
        response.raise_for_status()
        try:
            check_for_redirect(response)
            with open(f'./books/id{book_id}.txt', 'wb') as file:
                file.write(response.content)
        except requests.exceptions.HTTPError:
            print(f'Book #{book_id} not found')


if __name__ == '__main__':
    main()
