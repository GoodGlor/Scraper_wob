from aiohttp.client_exceptions import *
from bs4 import BeautifulSoup as bs
from fake_headers import Headers
from get_proxy import ListProxy
import csv
import random
import aiohttp
import asyncio
import os
import gc

PROXY_LIST = ListProxy()


class CollectInfo:
    """
    Collect info per one link
    """

    def __init__(self, max_connections: int, category_name: str, sub_category_books: str, all_data: list):
        self.user_agent = Headers().generate()['User-Agent']  # select random user agent
        self.category = category_name
        self.sub_category = sub_category_books
        self.all_links_and_data = all_data
        self.limit_connections = max_connections

    @staticmethod
    def get_proxy() -> str or bool:
        """
        Get random proxy
        :return: random proxy
        """
        try:
            return random.choice(PROXY_LIST.main())
        except IndexError:
            print('No proxy in list')
            return False

    def write_to_file(self, all_data: tuple, first_call: bool) -> None:
        '''
        Write data to file
        :param first_call: first time call function
        :param all_data: Take all data witch collected
        :return: None
        '''
        current_path = os.getcwd()
        path_to_file = f'{current_path}/{self.category}/{self.sub_category}/result.csv'
        with open(path_to_file, 'a+') as file:
            head = (
                'Sku', 'Product_url', 'EAN', 'ISBN13', 'ISBN10', 'Title', 'Condition', 'Author', 'Binding_type',
                'Publisher',
                'Category', 'Stock', 'AuthorBiography', 'Summary', 'Reviews', 'Image', 'RRP', 'Price')
            writer = csv.DictWriter(file, head)
            if first_call:
                file.seek(0)
                file.truncate(0)
                writer.writeheader()
            writer.writerows(all_data)

    @staticmethod
    async def collect_info_per_link(text_response, data: dict, title: str, author: str, index: int,
                                    count_links_to_scrape: int) -> dict:
        """
        Collect info form one page
        :param text_response: html response
        :param data: values witch collected before in class CollectedLinks
        :param title: title of page
        :param author: author of page
        :param index: current index of values
        :param count_links_to_scrape: total to scrape links
        :return: all collected data witch need
        """

        soup = bs(text_response, 'lxml')

        image = soup.find('img').get('src')

        data.update({'Image': image})

        try:
            rpr = soup.find('div', class_='rrp').text.replace('New RRP', '').replace('£', '')
            data.update({'RRP': rpr})
        except AttributeError:
            data.update({'RRP': None})

        try:
            reviews = [review for review in soup.find_all('section', class_='collapse') if
                       review.find('header').text == f'{title} Reviews'][0]
            data.update({'Reviews': reviews})
        except IndexError:
            data.update({'Reviews': None})

        try:
            author_biography = [biography for biography in soup.find_all('section', class_='collapse') if
                                biography.find('header').text == f'About {author}'][0]
            data.update({'AuthorBiography': author_biography})
        except IndexError:
            data.update({'AuthorBiography': None})

        try:
            summary = [summ for summ in soup.find_all('section', class_='collapse') if
                       summ.find('header').text == f'{title} Summary'][0]
            data.update({'Summary': summary})
        except IndexError:
            data.update({'Summary': None})

        all_attributes = soup.find('div', class_='attributes').find_all('div', class_='attribute')
        for attribute in all_attributes:
            label = attribute.find('label').text

            if label == 'ISBN 13':
                ean = attribute.find('div').text
                isbn_13 = attribute.find('div').text
                data.update({'EAN': ean, 'ISBN13': isbn_13})

            if label == 'ISBN 10':
                isbn_10 = attribute.find('div').text
                data.update({'ISBN10': isbn_10})

            if label == 'Publisher':
                publisher = attribute.find('div').text
                data.update({'Publisher': publisher})
        print(f'Collected info from link {index}/{count_links_to_scrape}')
        return data

    async def get_info_per_link(self, session, data: dict, url: str, title: str, author: str, index: int,
                                count_links_to_scrape: int):
        """
        Create a session and get response for server
        :param session: take session
        :param data: values witch collected before in class CollectedLinks
        :param url: link to scrape
        :param title: title of page
        :param author:author of page
        :param index:current index of values
        :param count_links_to_scrape: total to scrape links
        :return: func -> collect_info_per_link
        """
        headers = {
            'user-agent': self.user_agent
        }
        proxy = self.get_proxy()
        if not proxy:
            return False

        try:
            async with session.get(url, proxy=proxy, headers=headers, timeout=20) as response:
                await asyncio.sleep(1)
                text_response = await response.text()
                return await self.collect_info_per_link(text_response, data, title, author, index,
                                                        count_links_to_scrape)
        except (
                ClientHttpProxyError, ContentTypeError, ClientProxyConnectionError, ClientConnectorError,
                ClientResponseError, AttributeError):
            print('Not valid proxy')
            PROXY_LIST.delete_invalid_proxy(proxy, PROXY_LIST.all_poxy_list())
            return await self.get_info_per_link(session, data, url, title, author, index, count_links_to_scrape)
        except Exception as error:
            # print(f'{"-" * 15}>', error)
            return await self.get_info_per_link(session, data, url, title, author, index, count_links_to_scrape)
        #                                           # If some another errors call again this func with another proxy

    async def create_tasks(self, all_data: tuple, index: int, count_links_to_scrape: int):
        '''
        Create async tasks for scraping
        :param count_links_to_scrape:
        :param index:
        :param all_data: some values (result of class CollectedLinks) witch collected before, and links
        :return: All collected data per selected links
        '''
        connector = aiohttp.TCPConnector(limit=self.limit_connections, ssl=False, force_close=True)

        tasks = []
        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
            for i, data in enumerate(all_data):
                url = data['Product_url']
                title = data['Title']
                author = data['Author']
                tasks.append(
                    self.get_info_per_link(session, data, url, title, author, i + index, count_links_to_scrape))
            all_values = await asyncio.gather(*tasks)
            return all_values

    def main(self) -> None or bool:

        '''
        Run full class
        :return: None
        '''
        all_links = self.all_links_and_data
        for index in range(0, len(all_links), 1000):
            try:
                all_values = asyncio.run(self.create_tasks(all_links[0:1000], index, len(all_links)))
                if index == 0:
                    self.write_to_file(all_values, True)
                else:
                    self.write_to_file(all_values, False)
            except AttributeError:
                return False

            del all_values
            del all_links[0:1000]
            gc.collect()
