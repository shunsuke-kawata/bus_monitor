import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from lxml import html,etree
import schedule
import csv
import io
import numpy as np
from datetime import datetime

load_dotenv()

LINE_NOTIFY_TOKEN = os.getenv('LINE_NOTIFY_TOKEN')

BUS_BASE_URL = 'https://www.bushikaku.net/search/'
LINE_NOTIFY_URL = 'https://notify-api.line.me/api/notify'

CSV_PATH = './schedule.csv'

destination_list = [
    {
        'destination': 'fukuoka_osaka/',
        'description':'福岡-大阪',
        'day': '20240614'
    },
    {
        'destination': 'fukuoka_kyoto/',
        'description':'福岡-京都',
        'day': '20240614'
    },
    {
        'destination': 'osaka_ishikawa/',
        'description':'大阪-石川',
        'day': '20240615'
    },
    {
        'destination': 'kyoto_ishikawa/',
        'description':'京都-石川',
        'day': '20240615'
    },
    {
        'destination': 'ishikawa_osaka/',
        'description':'石川-大阪',
        'day': '20240615'
    },
    {
        'destination': 'ishikawa_kyoto/',
        'description':'石川-京都',
        'day': '20240615'
    },
    {
        'destination': 'osaka_fukuoka/',
        'description':'大阪-福岡',
        'day': '20240616'
    },
    {
        'destination': 'kyoto_fukuoka/',
        'description':'京都-福岡',
        'day': '20240616'
    },
    {
        'destination': 'fukuoka_kagawa/',
        'description':'福岡から香川',
        'day': '20240707'
    },
    {
        'destination': 'kagawa_fukuoka/',
        'description':'香川から福岡',
        'day': '20240708'
    }
]

scraping_headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

notify_headers = {
    'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'
}

colorlist = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf']

#1のときのみRhineで通知
send_line_flag = 1

def parse_html(url,destination_info):
    destination = destination_info['destination']
    day = destination_info['day']
    res = requests.get(f'{url}{destination}{day}',headers=scraping_headers)
    soup_parser = BeautifulSoup(res.text, 'lxml')
    lxml_data = etree.HTML(str(soup_parser))
    clearfix_elements = lxml_data.xpath('//li[@class="clearfix"]')
    
    price_list = []
    for element in clearfix_elements:
        
        # fee_structureを取得
        fee_structures = element.xpath('.//div[@class="fee_structure"]')
        for fee_structure in fee_structures:
            include = fee_structure.xpath('.//tr[@class="include"]')
            for i in include:
                price = i.xpath('.//td[@class="amount_box"]')[0][0][0][0]
                if not (price.text is None):
                    price_list.append(price.text)
    return price_list
                    
def get_min_data(price_list):
    
    min = price_list[0]
    for price in price_list:
        if(int(min[:min.find('円')].replace(',', ''))>int(price[:price.find('円')].replace(',', ''))):
            min = price
    return int(min[:min.find('円')].replace(',', ''))

def notify_data(path=CSV_PATH):
    with open(path, 'r', encoding='utf-8') as f:  # ファイルをutf-8で開く
        reader = csv.reader(f)
        csv_data = [x for x in reader]
    
    plot_csv_data= np.array(csv_data).T
    message_list = []

    for datum in plot_csv_data[1:]:
        destination = datum[0]
        transition_data = f'{destination}の最安値\n{datum[-4]}→{datum[-3]}→{datum[-2]}→{datum[-1]}'
        
        #変更があった区間を通知
        if(datum[-4]!=datum[-3] or datum[-3]!=datum[-2]or datum[-2]!=datum[-1]):
            changed_data = {'message':f'\n更新があった区間\n{transition_data}'}
            res = requests.post('https://notify-api.line.me/api/notify', headers=notify_headers,data=changed_data)
        message_list.append(transition_data)
    
    message = '\n'.join(message_list)
    message_data = {'message':f'\n{csv_data[-4][0]}→{csv_data[-1][0]}\n{message}'}
    res = requests.post('https://notify-api.line.me/api/notify', headers=notify_headers,data=message_data)
    print(res.status_code)
        
def write_csv(data_to_write,path=CSV_PATH): 
    with open(path, 'r') as f:
        reader = csv.reader(f)
        data = [x for x in reader]
    data.append(data_to_write)
    
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(data[0])
        writer.writerows(data[-10:])
        
def main():
    global send_line_flag
    
    japan_datetime = datetime.now().strftime("%m/%d %H:%M")
    row = [japan_datetime]
    for destination_info in destination_list:
        price_list = parse_html(url=BUS_BASE_URL,destination_info=destination_info)
        min = get_min_data(price_list=price_list)
        time.sleep(1)
        row.append(min)
    
    write_csv(row)
    print("書き込み完了")

    #8時間ごとに通知
    if(send_line_flag==1):
        notify_data()

    send_line_flag = (send_line_flag+1)%4

if __name__=='__main__':
    print("started monitoring")
    notify_data()

    #1時間ごとに実行する
    schedule.every(1).hours.do(main) 
    while True:
        schedule.run_pending()
        time.sleep(1)