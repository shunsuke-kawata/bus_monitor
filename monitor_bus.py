import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

load_dotenv()

LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')

BUS_BASE_URL = 'https://www.bushikaku.net/search/'


destination_list = [
    {
        'destination': 'fukuoka_osaka/',
        'day': '20240614/'
    },
    {
        'destination': 'fukuoka_kyoto/',
        'day': '20240614/'
    },
    {
        'destination': 'osaka_ishikawa/',
        'day': '20240615/'
    },
    {
        'destination': 'kyoto_ishikawa/',
        'day': '20240615/'
    },
    {
        'destination': 'ishikawa_osaka/',
        'day': '20240615/'
    },
    {
        'destination': 'ishikawa_kyoto/',
        'day': '20240615/'
    },
    {
        'destination': 'osaka_fukuoka/',
        'day': '20240616/'
    },
    {
        'destination': 'kyoto_fukuoka/',
        'day': '20240616/'
    }
]

#ユーザーエージェント情報
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

#j_sys_search_link clearfix

def parse_html(url,destination_info):
    destination = destination_info['destination']
    day = destination_info['day']
    print(f'{url}{destination}{day}')
    res = requests.get(f'{url}{destination}{day}',headers=headers)
    soup_parser = BeautifulSoup(res.text, 'html.parser')
    clearfix = soup_parser.find_all('li',class_='clearfix')
    fee_structure = soup_parser.find_all('div',class_='fee_structure')
    print(fee_structure)
    
    
    

def main():
    for destination_info in destination_list:
        parse_html(BUS_BASE_URL,destination_info)

if __name__=='__main__':
    main()
