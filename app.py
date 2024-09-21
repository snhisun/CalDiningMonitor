import os
from flask import Flask, render_template, request
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client['caldining_app']
users_collection = db['users']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'subscribe' in request.form:
            # Subscription form submitted
            email = request.form['email']
            dishes = request.form['dishes']
            dishes_list = [dish.strip() for dish in dishes.split(',')]

            # Save to MongoDB
            user = {
                'email': email,
                'dishes': dishes_list,
                'subscribed': True
            }
            users_collection.insert_one(user)
            return 'You have been subscribed!'
        elif 'unsubscribe' in request.form:
            # Unsubscribe form submitted
            email = request.form['email']
            result = users_collection.update_one(
                {'email': email, 'subscribed': True},
                {'$set': {'subscribed': False}}
            )
            if result.modified_count > 0:
                return 'You have been unsubscribed.'
            else:
                return 'Email not found or already unsubscribed.'

    return render_template('index.html')

@app.route('/unsubscribe/<user_id>')
def unsubscribe(user_id):
    try:
        # Update the user's subscription status to False (unsubscribe)
        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'subscribed': False}})
        return 'You have been unsubscribed successfully.'
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
