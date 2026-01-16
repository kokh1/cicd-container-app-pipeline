#code for the flask-app-template

#import the needed libraries

from dotenv import load_dotenv
import os
import requests
from flask import Flask, jsonify, redirect
from flask import Response
import json

#load environment variables from .env file

load_dotenv()

#example usage of envirnoment varaibles:

PORT = int(os.getenv('PORT', 5000))

#set up Flask app

app = Flask(__name__)

#define route for the homepage

@app.route('/')
def home():
    #return f"Hello, World! This Flask app is running on port {os.getenv('PORT', 5000)}."
    return redirect('/joke') #redirect straight to the joke

#define route for getting a random joke from an external API

@app.route('/joke')
def joke():
   response = requests.get('https://official-joke-api.appspot.com/jokes/random')
   joke = response.json()
   #reorder the keys for the joke response to return in
   ordered_joke = {
      "setup": joke.get("setup"),
      "punchline": joke.get("punchline"),
      "type": joke.get("type"),
   }
   return Response(
      json.dumps(ordered_joke),
      mimetype='application/json'
   )

#run the app on the port from the env variable, or default to 5000

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=PORT)
   



