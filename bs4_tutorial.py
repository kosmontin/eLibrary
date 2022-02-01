import requests

from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')
post_title = soup.find('article').find('h1').text
post_image = soup.find('article').find('img').attrs['src']
post_text = soup.find('article').find('div', class_='entry-content').text
print(post_title, post_image, post_text, sep='\n')