import os

import requests


def main():
    url = 'http://tululu.org/txt.php'

    if not os.path.exists('books'):
        os.makedirs('books')

    for book_id in range(1, 11):
        response = requests.get(url, params={'id': book_id})
        response.raise_for_status()
        if response.ok:
            with open(f'./books/id{book_id}.txt', 'wb') as file:
                file.write(response.content)


if __name__ == '__main__':
    main()
