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

    return render_template('index.html')

@app.route('/unsubscribe/<user_id>')
def unsubscribe(user_id):
    users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'subscribed': False}})
    return 'You have been unsubscribed.'

if __name__ == '__main__':
    app.run(debug=True)
