import csv
import os
import gc


class ListProxy:
    def __init__(self):
        self.current_directory = os.getcwd()

    def all_poxy_list(self) -> list:
        with open(f'{self.current_directory}/proxy.csv', 'r') as file:
            reader = csv.DictReader(file, fieldnames=['proxy'])
            proxies = []
            for proxyy in reader:
                if proxyy['proxy'] != 'proxy':
                    proxies.append(proxyy['proxy'])
            return proxies

    def delete_invalid_proxy(self, proxy: str, proxy_list: list):
        with open(f'{self.current_directory}/proxy.csv', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=['proxy'])
            new_proxy_list = [{'proxy': row} for row in proxy_list if proxy != row]
            writer.writeheader()
            writer.writerows(new_proxy_list)

            del new_proxy_list
            gc.collect()

    def main(self) -> list:
        return self.all_poxy_list()


if __name__ == '__main__':
    get_proxy_list = ListProxy()
    get_proxy_list.main()
