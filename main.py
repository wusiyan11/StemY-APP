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

from flask import Flask, redirect, render_template, request

from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision


CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')


app = Flask(__name__)


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


@app.route('/upload_profile', methods=['GET', 'POST'])
def upload_profile():

    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    age = '17'

    # The kind for the new entity.
    kind = 'People'

    # The name/ID for the new entity.
    name = 'David'

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind)

    # Construct the new entity using the key. Set dictionary values for entity
    # keys blob_name, storage_public_url, timestamp, and joy.
    entity = datastore.Entity(key)
    entity['name'] = name
    entity['age'] = age

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # Redirect to the home page.
    return redirect('/')


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
