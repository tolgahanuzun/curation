import requests
from bs4 import BeautifulSoup

from utils import avaible_link

utopian_link = 'https://utopian.rocks/queue'
exclude = 'https://steemit.com/utopian-io/@amosbastian/developing-the-new-utopian-bot'

def run():
    r  = requests.get(utopian_link)
    data = r.text

    soup = BeautifulSoup(data)
    contributions = soup.find('div', {'class' :'contributions'})
    data = []
    for link in soup.find_all('a'):
        link = link.get('href')
        if avaible_link(link):
            data.append(link)
    if exclude in data:
        data.remove(exclude)
    return data
