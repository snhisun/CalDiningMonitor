import os
import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime

def scrape_menu():
    # MongoDB setup
    MONGO_URI = os.environ.get('MONGO_URI')
    client = pymongo.MongoClient(MONGO_URI)
    db = client['caldining_app']
    menu_collection = db['menu_items']

    # Scrape the CalDining website
    url = 'https://dining.berkeley.edu/menus/'
    response = requests.get(url)
    if response.status_code != 200:
        print('Failed to retrieve the menu page.')
        return
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract today's date
    today = datetime.now().strftime('%a, %b %d')  # e.g., 'Sat, Sep 21'

    # Find all 'li' elements with class 'recip'
    menu_items = []
    menu_list = soup.find_all('li', class_='recip')

    for item in menu_list:
        dish_name = item.find('span').text.strip()
        # Find location and time
        location_info = item.find_parent('li', class_='location-name')
        if location_info:
            location_name = location_info.find('span', class_='cafe-title').text.strip()
            times_div = location_info.find('div', class_='times')
            if times_div:
                times = ' '.join([span.text.strip() for span in times_div.find_all('span')])
            else:
                times = ''
            date = location_info.find('span', class_='serve-date').text.strip()
            menu_items.append({
                'dish_name': dish_name,
                'location': location_name,
                'times': times,
                'date': date
            })

    # Clear existing data for today
    menu_collection.delete_many({'date': today})

    # Insert new data
    if menu_items:
        menu_collection.insert_many(menu_items)
        print(f"Inserted {len(menu_items)} menu items.")
    else:
        print("No menu items found.")

if __name__ == '__main__':
    scrape_menu()
