import os
from flask import Flask
from flask import render_template
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)

@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/')
def home():
	return render_template('home.html')

@app.route('/secretsnapta')
def secretsnapta():
	return render_template('secretsnapta.html')

@app.route('/groups')
def groups():
	with open('static/namelist') as f:
		content = f.readlines()
	
	return render_template('groups.html', namelist=content)

@app.route('/feeds')
def feeds():
	return render_template('feeds.html')

#fix later
@app.route('/logout')
def logout():
	return login();


if __name__ == '__main__':
	app.run(debug=True)