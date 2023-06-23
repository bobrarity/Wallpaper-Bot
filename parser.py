import requests
from bs4 import BeautifulSoup
import os
import time
from dotenv import load_dotenv
import sqlite3
import re

load_dotenv()
URL = os.getenv('URL')
HOST = os.getenv('HOST')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
}



class CategoryParser:
    def __init__(self, url, name, category_id, pages = 3, download = False):
        self.url = url
        self.name = name
        self.category_id = category_id
        self.pages = pages
        self.download = download


    def get_html(self, i):
        html = requests.get(self.url + f'/page{i}', headers=HEADERS).text
        return html

    def get_soup(self, i):
        html = self.get_html(i)
        soup = BeautifulSoup(html, 'html.parser')
        return soup


    def get_data(self):
        for i in range(1, self.pages + 1):
            soup = self.get_soup(i)
            time.sleep(1)
            images_blocks = soup.find_all('a', class_='wallpapers__link')
            for block in images_blocks:
                try:
                    image_link = block.find('img', class_='wallpapers__image').get('src')
                    wallpapers_link = HOST + block.get('href')
                    page = requests.get(wallpapers_link, headers=HEADERS).text
                    time.sleep(1)
                    page_soup = BeautifulSoup(page, 'html.parser')
                    resolution = page_soup.find_all('span', class_='wallpaper-table__cell')[1].get_text(strip=True)
                    image_link_v3 = image_link.replace('300x168', resolution)
                    print(image_link_v3)

                    database = sqlite3.connect('wallpapers.db')
                    cursor = database.cursor()
                    cursor.execute('''
                    INSERT OR IGNORE INTO images(image_link, category_id) VALUES (?,?);
                    ''', (image_link_v3, self.category_id))
                    database.commit()
                    database.close()


                    if self.download:
                        if self.name not in os.listdir():
                            os.mkdir(str(self.name))
                        responseImage = requests.get(image_link_v3, headers=HEADERS).content
                        image_name = image_link_v3.replace('https://images.wallpaperscraft.ru/image/single/', '')
                        with open(f'{self.name}/{image_name}', mode='wb') as file:
                            file.write(responseImage)



                except:
                    pass




def parsing():
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find('ul', class_='filters__list')
    filters = block.find_all('a', class_='filter__link')
    for f in filters:
        filter_link = HOST + f.get('href')
        print(filter_link)
        name = f.get_text(strip=True)
        print(name)
        true_name = re.search(r'[3]*[A-Za-zА-Яа-я]+', name)[0]
        print(true_name)
        pages = int(re.search(r'[0-9][0-9]+', name)[0]) // 15
        print(pages)

        if true_name == '60 Favorites':
            continue

        database = sqlite3.connect('wallpapers.db')
        cursor = database.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO categories(category_name) VALUES (?)
        ''', (true_name, ))
        database.commit()

        cursor.execute('''
        SELECT category_id FROM categories WHERE category_name = ?
        ''', (true_name, ))
        category_id = cursor.fetchone()[0]
        database.close()

        print(category_id)

        parser = CategoryParser(url=filter_link, name=true_name, category_id=category_id)
        parser.get_data()


parsing()




