import os
import pymongo
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def notify_users():
    # MongoDB setup
    MONGO_URI = os.environ.get('MONGO_URI')
    client = pymongo.MongoClient(MONGO_URI)
    db = client['caldining_app']
    users_collection = db['users']
    menu_collection = db['menu_items']

    # Get today's date
    today = datetime.now().strftime('%a, %b %d')  # e.g., 'Sat, Sep 21'

    # Get all menu items for today
    menu_items_cursor = menu_collection.find({'date': today})
    menu_items = list(menu_items_cursor)

    # Build a dictionary of dishes
    menu_dict = {}
    for item in menu_items:
        dish_name = item['dish_name']
        if dish_name not in menu_dict:
            menu_dict[dish_name] = []
        menu_dict[dish_name].append({
            'location': item['location'],
            'times': item['times']
        })

    # For each user
    users = users_collection.find({'subscribed': True})
    for user in users:
        email = user['email']
        favorites = user['dishes']
        matches = []

        for favorite in favorites:
            for dish in menu_dict:
                if favorite.lower() in dish.lower():
                    # Found a match
                    for item in menu_dict[dish]:
                        matches.append({
                            'dish_name': dish,
                            'location': item['location'],
                            'times': item['times']
                        })

        if matches:
            # Send email
            send_email(email, matches, user['_id'])

def send_email(to_email, matches, user_id):
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')

    # Email content
    subject = 'Your Favorite Dishes are Available Today!'
    body = 'Hello,\n\nThe following dishes are available today:\n\n'
    for match in matches:
        body += f"{match['dish_name']} at {match['location']} during {match['times']}\n"

    unsubscribe_link = f"https://{caldiningmonitor}.herokuapp.com/unsubscribe/{user_id}"
    body += f'\nTo unsubscribe, click here: {unsubscribe_link}'
    body += '\n\nBest regards,\nCalDining Notifier'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

if __name__ == '__main__':
    notify_users()
