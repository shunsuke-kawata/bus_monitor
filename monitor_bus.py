import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from lxml import html,etree
import schedule

load_dotenv()

LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')


BUS_BASE_URL = 'https://www.bushikaku.net/search/'
LINE_NOTIFY_URL = 'https://notify-api.line.me/api/notify'

destination_list = [
    {
        'destination': 'fukuoka_osaka/',
        'description':'福岡から大阪',
        'day': '20240614'
    },
    {
        'destination': 'fukuoka_kyoto/',
        'description':'福岡から京都',
        'day': '20240614'
    },
    {
        'destination': 'osaka_ishikawa/',
        'description':'大阪から石川',
        'day': '20240615'
    },
    {
        'destination': 'kyoto_ishikawa/',
        'description':'京都から石川',
        'day': '20240615'
    },
    {
        'destination': 'ishikawa_osaka/',
        'description':'石川から大阪',
        'day': '20240615'
    },
    {
        'destination': 'ishikawa_kyoto/',
        'description':'石川から京都',
        'day': '20240615'
    },
    {
        'destination': 'osaka_fukuoka/',
        'description':'大阪から福岡',
        'day': '20240616'
    },
    {
        'destination': 'kyoto_fukuoka/',
        'description':'京都から福岡',
        'day': '20240616'
    }
]

#ユーザーエージェント情報
scraping_headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

notify_headers = {
    'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'
}

def parse_html(url,destination_info):
    destination = destination_info['destination']
    day = destination_info['day']
    print(f'{url}{destination}{day}')
    res = requests.get(f'{url}{destination}{day}',headers=scraping_headers)
    soup_parser = BeautifulSoup(res.text, 'lxml')
    lxml_data = etree.HTML(str(soup_parser))
    clearfix_elements = lxml_data.xpath('//li[@class="clearfix"]')
    
    price_list = []
    for element in clearfix_elements:
        # platform_boxを取得
        platform_box = element.xpath('.//div[@class="platform_box"]')[0]
        
        # fee_structureを取得
        fee_structures = element.xpath('.//div[@class="fee_structure"]')
        for fee_structure in fee_structures:
            include = fee_structure.xpath('.//tr[@class="include"]')
            for i in include:
                price = i.xpath('.//td[@class="amount_box"]')[0][0][0][0]
                if not (price.text is None):
                    price_list.append(price.text)
    
    return price_list
                    
def nofity_line(destination_info,price_list):
    destination = destination_info['description']
    day = destination_info['day']
    
    text_body = '\n'.join(price_list)
    info = '_'.join([destination,day])
    return_text = '\n'.join([info,text_body])
    data = {'message': '\n'+f'{return_text}'}
    res = requests.post('https://notify-api.line.me/api/notify', headers=notify_headers,data=data)
    print(res.text)
    
def main():
    for destination_info in destination_list:
        price_list = parse_html(url=BUS_BASE_URL,destination_info=destination_info)
        print(price_list)
        nofity_line(destination_info=destination_info,price_list=price_list)
        time.sleep(5)

if __name__=='__main__':
    schedule.every(1).minutes.do(main) 
    while True:
        schedule.run_pending()  # 3. 指定時間が来てたら実行、まだなら何もしない
        time.sleep(1)