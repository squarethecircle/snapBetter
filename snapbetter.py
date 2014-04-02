from flask import Flask
from flask import render_template
from flask import session
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import jsonify
import whisperfeed
import sys
import backend
import logging
from os import listdir
from os.path import isfile, join

reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
app.secret_key = 'secretkey'

# Defaults to stdout
logging.basicConfig(level=logging.INFO)

# get the logger for the current Python module
log = logging.getLogger(__name__)

APP_STATIC = "static/"

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try: 
            log.info('Start reading database')
            # do risky stuff
            r = backend.login(request.form['username'], request.form['password'])
            if r != False:
                session['username'] = r['username']
                session['auth_token'] = r['auth_token']

                secretSanta = False
                for friend in r['friends']:
                    if friend['name'] == 'secret_snapta':
                        secretSanta = True
                        break

                session['snapta'] = secretSanta
                session['snapta_changed'] = 'false'


                backend.createSnapDir(session['username'])


                return redirect(url_for('home'))
            else:
                error = 'Invalid username/password combination'
                return render_template('login.html', error=error)
        except:

            # http://docs.python.org/2/library/sys.html
            _, ex, _ = sys.exc_info()
            log.error(ex.message)
    else:
        return render_template('login.html')


@app.route('/')
def home():
    error = None
    if not 'auth_token' in session:
        return redirect(url_for('login'))
    else:
        return render_template('home.html')

@app.route('/secretsnapta')
def secretsnapta():
    error = None
    if not 'auth_token' in session:
        error = 'Please log in'
        return render_template('login.html', error=error)
    else:
        return render_template('secretsnapta.html')

@app.route('/groups')
def groups():
    error = None
    if not 'auth_token' in session:
        error = 'Please log in'
        return render_template('login.html', error=error)
    else:

        
        return render_template('groups.html')

@app.route('/feeds')
def feeds():
    error = None
    if not 'auth_token' in session:
        error = 'Please log in'
        return render_template('login.html', error=error)
    else:
        return render_template('feeds.html')

#feed of all snaps
@app.route('/snapfeed')
def snapfeed():
    if not 'auth_token' in session:
        error = 'Please log in'
        return render_template('login.html', error=error)
    else:
        backend.updateSaveNewSnaps(session['username'], session['auth_token'])

        snappath = APP_STATIC + 'img/snaps/' + session['username']
        files = [ join(snappath, f) for f in listdir(snappath) if isfile(join(snappath,f)) ]
        return render_template('snapfeed.html', files=files)

@app.route('/logout')
def logout():
    error = None
    backend.deleteSnapDir(session['username'])
    session.pop('username', None)
    session.pop('auth_token', None)
    session.pop('snapta_changed', None)
    session.pop('snapta', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/requests', methods=['GET', 'POST'])
def requests():
    if request.method == 'POST':
        if request.form['request'] == 'isSnaptaFriend':
            r = backend.update(request.form['username'], request.form['auth_token'])
            print session['snapta_changed']
            if session['snapta_changed'] == 'false':
                if session['snapta'] == True:
                    return 'friends'
                else:
                    return 'nofriends'
            else:
                if session['snapta'] == True:
                    return 'nofriends'
                else:
                    return 'friends'

        elif request.form['request'] == 'makeFriend':   
            r = backend.makeFriend(request.form['username'], request.form['auth_token'], request.form['friend'])
            if r == 200:
                session['snapta_changed'] = 'true'

                return 'true'
            else:
                return 'false'
        elif request.form['request'] == 'deleteFriend':
            r = backend.deleteFriend(request.form['username'], request.form['auth_token'], request.form['friend'])
            
            if r == 200:
                session['snapta_changed'] = 'true'
                return 'true'
            else:
                return 'false'
        elif request.form['request'] == 'getFriends':
            r = backend.update(request.form['username'], request.form['auth_token'])
            return jsonify(r)


@app.route('/snaptachanged', methods=['GET'])
def snaptachanged():
    return session["snapta_changed"]



@app.route('/sendonewhisper', methods=['POST'])
def sendOneWhisper():
    backend.makeFriend(request.form['username'], request.form['auth_token'], 'whisper_feed')
    origAT = request.form['auth_token']
    origUN = request.form['username']

    r = backend.login('whisper_feed', 'Banvanphan2105!')
    at = r['auth_token']
    backend.makeFriend('whisper_feed', at, origUN)

    feed = whisperfeed.main()
    data = backend.encrypt_image(feed)
    r = backend.sendSnap('whisper_feed', at, data, [origUN], 10)
    session['auth_token'] = origAT
    session['username'] = origUN
    if r == 200:
        return "success"
    else:
        return "false"



if __name__ == '__main__':
    app.run(debug=True)