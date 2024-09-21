import os
import pymongo
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
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
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')
    FROM_EMAIL = os.environ.get('FROM_EMAIL')  # Your verified sender email

    if not SENDGRID_API_KEY or not FROM_EMAIL:
        print("SendGrid API key or FROM_EMAIL not set.")
        return

    # Email content
    subject = 'Your Favorite Dishes are Available Today!'
    body = 'Hello,\n\nThe following dishes are available today:\n\n'
    for match in matches:
        body += f"{match['dish_name']} at {match['location']} during {match['times']}\n"

    unsubscribe_link = f"https://{HEROKU_APP_NAME}.herokuapp.com/unsubscribe/{user_id}"
    body += f'\nTo unsubscribe, click here: {unsubscribe_link}'
    body += '\n\nBest regards,\nCalDining Notifier'

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email} with status code {response.status_code}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

if __name__ == '__main__':
    notify_users()
