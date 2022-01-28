import requests
from fake_headers import Headers
from bs4 import BeautifulSoup as bs


def collect_proxies_free_proxy() -> tuple or bool:
    url = 'https://free-proxy-list.net/'
    headers = Headers().generate()
    response = requests.get(url, headers=headers)

    soup = bs(response.text, 'lxml')
    table = soup.find('div', class_='table-responsive fpl-list').find('tbody')

    proxy_list = [
        f"{row.find('td').text}:{row.find('td').find_next('td').text}"
        for row in table
    ]
    return proxy_list