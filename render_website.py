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
        books_info = json.load(file)
    chunked_books_info = enumerate(chunked(books_info, books_per_page), start=1)
    os.makedirs('pages', exist_ok=True)

    for num_page, part_of_book in chunked_books_info:
        rendered_page = template.render(
            num_page=num_page,
            num_pages=math.ceil(len(books_info) / books_per_page),
            chunked_books_info=chunked(part_of_book, 2)
        )
        with open(f'pages/index{num_page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch(filepath='./templates', func=on_reload)
    server.watch(filepath='./books_info.json', func=on_reload)
    server.serve()
