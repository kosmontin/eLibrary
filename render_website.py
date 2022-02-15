import json
# from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('cards_template.html')

books_info = []
with open('books_info.json', 'r', encoding='utf-8') as file:
    books_info = json.load(file)

rendered_page = template.render(
    books_info=books_info,
    title='Книги'
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

# server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
# server.serve_forever()