# -*- coding: utf-8 -*-
"""
Created on Sun May  2 20:11:48 2021

@author: ELCOT
"""

import requests
import json
from flask import Flask, render_template, request, session, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'g'

app.config["MYSQL_HOST"] = "remotemysql.com"
app.config["MYSQL_USER"] = "l5T3J7NLMF"
app.config["MYSQL_PASSWORD"] = "XU6jM5qIVw"
app.config["MYSQL_DB"] = "l5T3J7NLMF"


mysql = MySQL(app)


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods = ["POST"])
def register():
   if request.method == "POST":
       name = request.form["name"]
       email = request.form["email"]
       mobileno = request.form["mobileno"]
       password = request.form["password"]
       cursor = mysql.connection.cursor()
       cursor.execute('INSERT INTO registrationData VALUES (NULL,% s,% s,% s,% s)',(name,email,mobileno,password))
       mysql.connection.commit()
       msg = 'You have Successfully Registered!'
   return render_template('home.html', msg = msg)
    
@app.route('/login', methods = ["POST", "GET"])
def login():
    global userid
    global account
    msg = ""
    if request.method == "POST":
        user_name = request.form['name']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM registrationData WHERE name = % s AND password = % s',(user_name, password),)
        account = cursor.fetchone()
        print (account)
        
        if account:
           session['loggedin'] = True
           session['id'] = account[0]
           userid = account[0]
           session['email'] = account[2]
           session['username'] = account[1]
           msg = 'You have Sucessfully Logged In!'
       
           return render_template('scan.html', msg = msg)
   
        else:
            msg = 'Incorrect User Name / Password'

    return render_template('login.html', msg = msg)

def ocr_space_url(url, overlay=False, api_key='50d04a4f1288957', language='eng'):
    """ OCR.space API request with remote file.
        Python3.5 - not tested on 2.7
    :param url: Image url.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    r = requests.post('https://api.ocr.space/parse/image',
                      data=payload,
                      )
    return r.content.decode()
     
@app.route('/upload', methods = ["POST"])
def upload_url():
    global output
    if request.method == "POST":
         url = request.form["url"]
         name = session["username"]
         email = session["email"]
         cursor = mysql.connection.cursor()
         cursor.execute('INSERT INTO saveURL VALUES(NULL,% s,% s,% s)',(name,email,url))
         mysql.connection.commit()
         test_url = ocr_space_url(url , language='eng')
         print(test_url)
         data=json.loads(test_url)
         output = data['ParsedResults'][0]['ParsedText']
         session['text'] = str(output)
    return render_template("scan.html", output = output)
            
@app.route('/save')
def save_text():
    name = session["username"]
    email = session["email"]
    text = session['text']
    new_text = text.replace("\n"," ").replace("\r","").replace(",", "")
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO saveText VALUES(NULL,% s,% s,% s)',(name,email,new_text))
    mysql.connection.commit()
    msg = 'Text Successfully Saved!'
    return render_template('scan.html', msg = msg)

@app.route('/view')
def view():
    name = session["username"]
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM saveURL WHERE name = % s',(name,)) 
    data = cursor.fetchone()
    url = data[3]
    return redirect(url)
    
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('useremail', None)
   session.pop('text', None)
   return render_template('home.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True,port=8080)