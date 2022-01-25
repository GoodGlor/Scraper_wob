from aiohttp.client_exceptions import *
from fake_headers import Headers
from get_proxy import ListProxy
import csv
import random
import requests
import aiohttp
import asyncio
import os
import gc

PROXY_LIST = ListProxy()


class CollectLinks:
    """
    Collect links and some data
    """

    def __init__(self, limit_connections: int, category: str, sub_category_books: str, url_link_category: str):
        self.url = url_link_category
        self.category = category
        self.sub_category = sub_category_books
        self.user_agent = Headers().generate()['User-Agent']
        self.limit = limit_connections

    def create_directory(self) -> None:
        """
        Create directory for save data
        :return: None
        """
        current_path = os.getcwd()
        if not os.path.exists(f'{current_path}/{self.category}'):
            os.mkdir(f'{current_path}/{self.category}')

        name_directory = f'{self.category}/{self.sub_category}'

        is_exist = os.path.exists(current_path + f'/{name_directory}')
        if not is_exist:
            os.mkdir(current_path + f'/{name_directory}')

    def write_to_file(self, all_data: list) -> None:
        """
        Write collected data to file
        :param all_data: Values witch collected
        :return: None
        """
        self.create_directory()
        current_path = os.getcwd()
        path_to_file = f'{current_path}/{self.category}/{self.sub_category}/{self.sub_category}.csv'

        with open(path_to_file, 'w') as file:
            head = (
                'Sku', 'Product_url', 'EAN', 'ISBN13', 'ISBN10', 'Title', 'Condition', 'Author', 'Binding_type',
                'Publisher',
                'Category', 'Stock', 'AuthorBiography', 'Summary', 'Reviews', 'Image', 'RRP', 'Price')
            writer = csv.DictWriter(file, head)
            writer.writeheader()
            writer.writerows(all_data)

    @staticmethod
    def get_proxy() -> str or bool:
        """
           Get random proxy
           :return: random proxy
        """
        try:
            return random.choice(PROXY_LIST.main())
        except IndexError:
            return False

    def get_num_of_result(self) -> int:
        """
        Get count of items for scraping.

        BUT SERVER SOMETIMES CAN ONLY GET <= 170 000 BOOKS PER ONE LINK

        :return: Total count to books
        """
        headers = {
            'x-locale': 'en-GB',
            'user-agent': self.user_agent
        }
        new_one_proxy = self.get_proxy()
        if not new_one_proxy:
            print('No proxy in list')
            return False

        try:
            proxies = {'http': new_one_proxy, 'https': new_one_proxy}
            response = requests.get(self.url, headers=headers, proxies=proxies, timeout=10)
            return response.json()['total']
        except Exception as error:
            # print(f'{"-" * 15}>', error)
            return self.get_num_of_result()

    @staticmethod
    def collect_link_data(response, offset: int, num_of_books: int) -> list:
        '''
        Collect data and links form api
        :param response: response form server
        :param offset: offset of page
        :param num_of_books: total num books to scrape
        :return: collected data
        '''
        all_data = []
        for row in response['results']:
            sku = row['sku']
            url_product = f"https://www.wob.com/en-gb/{row['urlSlug']}"
            stock = row['inventoryCount']
            condition = row['condition']
            title = row['title']
            author = row['author']
            price = row['price']
            binding_type = row['formatType']
            category = ''
            for cat in row['categoryBreadcrumbs']:
                category += f'{cat["name"]}/'
            all_data.append({
                'Sku': sku,
                'Product_url': url_product,
                'EAN': None,
                'ISBN13': None,
                'ISBN10': None,
                'Title': title,
                'Condition': condition,
                'Author': author,
                'Binding_type': binding_type,
                'Publisher': None,
                'Category': category,
                'Stock': stock,
                'AuthorBiography': None,
                'Summary': None,
                'Reviews': None,
                'Image': None,
                'RRP': None,
                'Price': price
            })

        print(f'Collected {offset}/{num_of_books} links')
        return all_data

    async def get_links_per_page(self, session, offset: int, num_of_books: int):
        """
        Create are session, and get response form server
        :param session:
        :param offset:
        :param num_of_books:
        :return: func -> collect_link_data
        """

        split_url = self.url.split('offset=72')

        url = split_url[0] + f'offset={offset}' + split_url[-1]

        headers = {
            'x-locale': 'en-GB',
            'user-agent': self.user_agent
        }

        proxy = self.get_proxy()
        try:
            async with session.get(url, proxy=proxy, headers=headers, timeout=15) as response:
                await asyncio.sleep(2)
                json_response = await response.json()
                return self.collect_link_data(json_response, offset, num_of_books)
        except (ClientHttpProxyError, ContentTypeError, ClientProxyConnectionError, ClientConnectorError):
            print('Not valid proxy')
            PROXY_LIST.delete_invalid_proxy(proxy, PROXY_LIST.all_poxy_list())
            return await self.get_links_per_page(session, offset, num_of_books)
        except Exception as error:
            # print(f'{"-"* 15}>', error)
            return await self.get_links_per_page(session, offset, num_of_books)

    async def get_all_links(self):
        """
        Collect all data per one category
        :return: all collected data
        """

        num_result = self.get_num_of_result()
        if not num_result:
            return False
        print(f'Num of books {num_result}')

        connector = aiohttp.TCPConnector(limit=self.limit, ssl=False, force_close=True)

        tasks = []

        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
            for offset in range(0, num_result, 72):
                tasks.append(self.get_links_per_page(session, offset, num_result))

            return await asyncio.gather(*tasks)

    def all_links(self) -> tuple or bool:
        try:
            all_data = asyncio.run(self.get_all_links())
        except TypeError:
            return False
        return tuple(all_data)

    def main(self):
        '''
        Save all collected data in one list, and write to file
        :return:
        '''
        try:
            links = self.all_links()
        except TypeError:
            return False
        all_data = [
            value
            for values in links
            for value in values
        ]

        self.write_to_file(all_data)

        del all_data
        gc.collect()
