# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
from datetime import datetime
import logging
import os
import json
import requests

from flask import Flask, redirect, render_template, request
from flask_cors import CORS, cross_origin

from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision


CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')


app = Flask(__name__)
CORS(app)

# class Categories(Object):
#     def __init__(self, key, content):
#         self.key = key
#         self.content = content


@app.route('/')
def homepage():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind='People')
    Profiles = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return json.dumps(Profiles)


@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    profile = request.get_json()
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    age = profile['age']

    # The kind for the new entity.
    grade = profile['grade']

    # The name/ID for the new entity.
    name = profile['name']

    gender = profile['gender']

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key('profile', name)

    # Construct the new entity using the key. Set dictionary values for entity
    # keys blob_name, storage_public_url, timestamp, and joy.
    entity = datastore.Entity(key)
    entity.update({
        'name': name,
        'grade': grade,
        'age': age,
        'gender': gender
        })

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # Redirect to the home page.
    return redirect('/')

@app.route('/getNews', methods=['GET'])
def getNews():   
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Categories')
    categories = list(query.fetch())
    headers = {'Ocp-Apim-Subscription-Key' : 'a34cfb783ed9495789c525c3336cf3d5'}
    catNews = {}
    count = 0;
    
    for category in categories:
        for i in range (0,3):
            url = 'https://api.cognitive.microsoft.com/bing/v5.0/news/search?q=inbody: ' + category['category'] + '&count=1&offset=0&mkt=en-us&safeSearch=Moderate'
            news = requests.get(url, headers=headers)
            catNews[count] = {'key' :category['category'], 'content' : json.loads(news.text)['value']}
            count += 1
    return json.dumps(catNews)

@app.route('/liked', methods=['POST'])
def liked():
    datastore_client = datastore.Client()
    likedLink = request.get_json()
    name = likedLink['name']
    url = likedLink['url']
    category = likedLink['key']
    timestamp = datetime.now()
    history = datastore_client.key('track')
    entity = datastore.Entity(history)
    entity.update({
        'name': name,
        'sourceURL': url,
        'timestamp': timestamp,
        'category': category
        })
    datastore_client.put(entity)
    return json.dumps({'saved': True})

@app.route('/delete', methods=['POST'])
def delete():
    deleteKey = request.get_json()['kind']
    datastore_client = datastore.Client()
    key = datastore_client.key(deleteKey, 5720147234914304)
    datastore_client.delete(key)
    return json.dumps({'deleted': True})


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
