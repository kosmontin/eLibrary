import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('./templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('cards_template.html')
    books_info = []
    with open('books_info.json', 'r', encoding='utf-8') as file:
        books_info = json.load(file)
    rendered_page = template.render(
        chunked_books_info=chunked(books_info, 2),
        title='Книги'
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch(filepath='./templates', func=on_reload)
    server.watch(filepath='./books_info.json', func=on_reload)
    server.serve()
