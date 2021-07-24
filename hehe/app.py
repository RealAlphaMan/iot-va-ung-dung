from flask import json, render_template, url_for, redirect, request, Flask, jsonify, send_file, send_from_directory
from pymongo import MongoClient
import textwrap
import datetime
import os
import shutil

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def index():

    return render_template('hello.html')

if __name__ == '__main__':
    app.run(port=5002)