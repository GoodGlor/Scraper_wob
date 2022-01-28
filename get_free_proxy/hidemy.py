import requests
from fake_headers import Headers
from bs4 import BeautifulSoup as bs


def get_proxy():
    headers = Headers().generate()
    url = 'https://hidemy.name/en/proxy-list/?country=ALARAMAUBDBYBEBZBTBOBRBGKHCMCACLCOCWCYCZDOECEGGQFRGEDEGHGTHNHKINIDIRIQIEILITKZKEKRLALYLTMYMXMDMNMZNPNLNINGNOPKPEPHPLPTPRRORURSSGSKSIZAESCHTWTJTHTRUAGBUSVEVNVG&maxtime=1000&type=s#list'
    response = requests.get(url, headers=headers)
    soup = bs(response.text, 'lxml')
    table_ips = soup.find('table').find('tbody').find_all('td')
    ipis = []
    for i in range(len(table_ips)):
        if i % 7 == 0:
            ip = table_ips[i].text
            port = table_ips[i + 1].text
            ipis.append(f'{ip}:{port}')
    return ipis
