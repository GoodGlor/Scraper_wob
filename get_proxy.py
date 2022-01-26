import os
import gc


class ListProxy:
    def __init__(self):
        self.current_directory = os.getcwd()

    def all_poxy_list(self) -> list:
        with open(f'{self.current_directory}/proxy.txt', 'r') as file:
            proxies = [proxy.strip()
                       for proxy in file.readlines()
                       ]
            return proxies

    def delete_invalid_proxy(self, proxy: str, proxy_list: list):
        with open(f'{self.current_directory}/proxy.txt', 'w') as file:
            proxy_list = [pr + '\n'
                          for pr in proxy_list
                          if proxy != pr]

            file.writelines(proxy_list)

            del proxy_list
            gc.collect()

    def main(self) -> list:
        return self.all_poxy_list()


if __name__ == '__main__':
    get_proxy_list = ListProxy()
    get_proxy_list.main()
