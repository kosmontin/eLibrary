import json
import math
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    books_per_page = 20
    env = Environment(
        loader=FileSystemLoader('./templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('cards_template.html')
    with open('books_info.json', 'r', encoding='utf-8') as file:
        books = json.load(file)
    chunked_books = enumerate(chunked(books, books_per_page), start=1)
    os.makedirs('pages', exist_ok=True)

    for page_num, books_part in chunked_books:
        rendered_page = template.render(
            page_num=page_num,
            pages_num=math.ceil(len(books) / books_per_page),
            chunked_books=chunked(books_part, 2)
        )
        with open(f'pages/index{page_num if page_num > 1 else ""}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch(filepath='./templates', func=on_reload)
    server.watch(filepath='./books_info.json', func=on_reload)
    server.serve()
