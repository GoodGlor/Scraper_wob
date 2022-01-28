import csv
import time

import requests

from hidemy import get_proxy
from free_proxy import collect_proxies_free_proxy
import aiohttp
import asyncio
from fake_headers import Headers

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def write_proxy(data):
    with open('proxy_list.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=['proxy'])
        writer.writeheader()
        writer.writerows(data)


def concatenate_proxy_lists():
    import requests

    proxy_list_1 = get_proxy()
    proxy_list_2 = collect_proxies_free_proxy()
    # full_list = proxy_list_1 + proxy_list_2
    # return tuple(full_list)

    r = requests.get(
        'http://list.didsoft.com/get?email=artem.levkovich0011@gmail.com&pass=rsesr8&pid=http3000&showcountry=no&https=yes&level=1|2|3')
    list_proxy = list(map(lambda x: x, r.text.split()))
    list_proxy += proxy_list_1
    list_proxy += proxy_list_2
    return tuple(list_proxy)


async def validation_proxy(session, proxy):
    url = 'http://lumtest.com/myip.json'
    try:
        async with session.get(url, proxy=proxy, timeout=6) as response:
            await asyncio.sleep(1)
            await response.json()
            print(f'Valid proxy -> {proxy}')
            return proxy.replace('http://', '')
    except Exception as e:
        # print(e)
        return False


async def create_tasks(proxy_list):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for proxy in proxy_list:
            proxy = f'http://{proxy}'
            tasks.append(validation_proxy(session, proxy))
        collected_proxy = await asyncio.gather(*tasks)
        all_proxy = []
        for proxy in collected_proxy:
            if proxy:
                all_proxy.append({'proxy': proxy})
        write_proxy(all_proxy)


def main():
    proxy_list = concatenate_proxy_lists()
    asyncio.run(create_tasks(proxy_list))


class TextProxy:
    def __init__(self):
        # self.url = url
        us = Headers().generate()['User-Agent']
        self.headers = {
            'x-locale': 'en-GB',
            'user-agent': us
        }

    @staticmethod
    def list_proxy():
        with open('proxy_list.csv', 'r') as file:
            reader = csv.DictReader(file, fieldnames=['proxy'])
            proxy_list = [row['proxy'] for row in reader if row['proxy'] != 'proxy']
            return tuple(proxy_list)

    @staticmethod
    def write_to_file(valid_proxy):
        with open('proxy.txt', 'a') as ff:
            ff.write(valid_proxy.replace('http://', '') + '\n')

    @staticmethod
    def read_valid_proxies():
        with open('proxy.txt', 'r') as ff:
            proxies = [row.strip() for row in ff.readlines()]
            return proxies

    def make_request(self, proxy):
        url = f'https://www.wob.com/en-gb'
        headers = self.headers
        proxy = f"http://{proxy}"
        proxies = {'http': proxy, 'https': proxy}
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=4, verify=False)
            if r.status_code == 200:
                return proxy
        except:
            return False

    def make_requests(self):
        valid_proxies = []
        proxy_already_in_list = self.read_valid_proxies()

        list_proxy = self.list_proxy()
        for i, proxy in enumerate(list_proxy):
            new_one = self.make_request(proxy)
            if new_one not in valid_proxies:
                if new_one not in proxy_already_in_list:
                    if not new_one:
                        continue
                    print(f'Good one {i + 1}/{len(list_proxy)}')
                    self.write_to_file(new_one)

    def main(self):
        self.make_requests()


if __name__ == '__main__':
    while True:
        main()
        validataion = TextProxy()
        validataion.main()
        del validataion
        time.sleep(400)
