import requests
import hashlib
import json
import sys
import time
import os
import shutil
import tempfile
from Crypto.Cipher import AES
import zipfile
import numpy as np
# import cv2
import shutil
import uuid
from requests_toolbelt import MultipartEncoder
import encode
import urllib2
# import httplib2
from urlgrabber.keepalive import HTTPHandler
import sha
 
APP_STATIC='static/'
API_URL='https://feelinsonice-hrd.appspot.com/'
AES_KEY='M02cnQ51Ji97vwT4'
STATIC_TOKEN='m198sOkJEn37DjqZ32lpRu76xmw288xSQ9'
HEADERS={'User-agent': 'Snapchat/6.1.2 (iPhone5,1; iOS 7.1; gzip)'}
 
def register(username, email, password, age, birthday):
	params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'email':email,'password':password,'age':int(age),'birthday':birthday}
	r=requests.post(API_URL+'bq/register',data=params,headers=HEADERS)
	timerec=int(time.time())
	if (r.json().get('logged')==False):
			return False
	if (r.json().get('captcha')!=None):
		params={'username':email,'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time()))}
		r=requests.post(API_URL+'bq/get_captcha',data=params,headers=HEADERS)
		with tempfile.NamedTemporaryFile(dir=APP_STATIC) as f:
			f.write(r.content)
			imagezip=zipfile.ZipFile(f)
			result=captchaSolver(imagezip)
		params={'captcha_id':email+'~'+timerec,'captcha_solution':result,'username':email,'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time()))}
		r=requests.post(API_URL+'bq/solve_captcha',data=params,headers=HEADERS)
	if (r.status_code!=200):
		return False
	token=r.json().get('token')
	params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'email':email,'username':username}
	r=requests.post(API_URL+'ph/registeru',data=params,headers=HEADERS)
	if (r.json().get('logged')==False):
		return False
	return r.json()
 
def login(username,password):
	params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'username':username,'password':password}
	r=requests.post(API_URL+'bq/login',data=params,headers=HEADERS)
	if (r.json().get('logged')==False):
		return False
	return r.json()

def update(username,auth_token):
	params={'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'username':username}
	r=requests.post(API_URL+'/bq/updates',data=params,headers=HEADERS)
	return r.json()

def encrypt_image(s):
	s =s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
	cipher = AES.new(AES_KEY, AES.MODE_ECB, "")
	#newfile=tempfile.NamedTemporaryFile(dir=APP_STATIC)

	return cipher.encrypt(s)

def decrypt_image(s):
	cipher = AES.new(AES_KEY, AES.MODE_ECB, "")
	return cipher.decrypt(s)
 
def request_token(auth_token, timestamp):
	secret = "iEk21fuwZApXlz93750dmW22pw389dPwOk"
	pattern = "0001110111101110001111010101111011010001001110011000110001000110"
	first = hashlib.sha256(secret + auth_token).hexdigest()
	second = hashlib.sha256(str(timestamp) + secret).hexdigest()
	bits = [first[i] if c == "0" else second[i] for i, c in enumerate(pattern)]
	return "".join(bits)
 
def requestVerificationCode(username,auth_token,phoneNumber):
	params={'username':username,'action':'updatePhoneNumber','countryCode':'US','phoneNumber':phoneNumber,'req_token':request_token(auth_token,int(time.time())),'timestamp':int(time.time())}
	r=requests.post(API_URL+'ph/settings',data=params,headers=HEADERS)
	return r.json()

def verifyCode(username,auth_token,code):
	params={'username':username,'action':'verifyPhoneNumber','code':code,'req_token':request_token(auth_token,int(time.time())),'timestamp':timestamp}
	r=requests.post(API_URL+'ph/settings',data=params,headers=HEADERS)
	return r.json()

def makeFriend(username, auth_token, friend):
	params={'username': username, 'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'action': 'add', 'friend': friend}
	r=requests.post(API_URL+'ph/friend',data=params,headers=HEADERS)
	return r.status_code

def deleteFriend(username, auth_token, friend):
	params={'username': username, 'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'action': 'delete', 'friend': friend}
	r=requests.post(API_URL+'ph/friend',data=params,headers=HEADERS)
	return r.status_code
 
def fetchSnap(username, auth_token, idnum):
	params={'username':username, 'req_token':request_token(auth_token,int(time.time())),'timestamp': int(time.time()), 'id': idnum }
	r=requests.post(API_URL+'ph/blob',data=params,headers=HEADERS)
	return r.content

#fetches IDs of unopened snaps
def unopenedIds(username, auth_token):
	r = update(username, auth_token)['snaps']
	unseen = []
	for snap in r:
		if 't' in snap:
			if snap['t'] > 0:
				if snap['m'] == 0:
					unseen.append(snap['id'])
	return unseen


#fetches and decrypts Snap
def fetchDecryptSnap(username, auth_token, idnum):
	return decrypt_image(fetchSnap(username, auth_token, idnum))

#fetch and decrypt all unopened snaps
def fetchUnopenedSnaps(username, auth_token):
	snaps = []
	for idnum in unopenedIds(username,auth_token):
		snaps.append([idnum, fetchDecryptSnap(username, auth_token, idnum)])
	return snaps

#login, fetch, and decrypt unopened snaps
def logFetchNew(username, password):
	return fetchUnopenedSnaps(username, login(username, password)['auth_token'])


#fetches all snaps and saved unsaved ones
def updateSaveNewSnaps(username, auth_token):
	snaps = fetchUnopenedSnaps(username, auth_token)
	for snap in snaps:
		if not os.path.exists(APP_STATIC + "img/snaps/" + username + '/' + snap[0] + ".jpg"):
			f = open(APP_STATIC + "img/snaps/" + username + '/' + snap[0] + ".jpg", "w")
			f.write(snap[1])
			f.close()

def createSnapDir(username):
	if not os.path.exists(APP_STATIC + "img/snaps/" + username):
		os.mkdir(APP_STATIC + "img/snaps/" + username)

def deleteSnapDir(username):
	if os.path.exists(APP_STATIC + "img/snaps/" + username):
		shutil.rmtree(APP_STATIC + "img/snaps/" + username)


def sendSnap(username, auth_token, data2, listoffriends, length):
	media_id=username.capitalize()+'~'+str(uuid.uuid1())
	keepalive_handler=HTTPHandler()
	# opener=urllib2.build_opener(keepalive_handler)
	# urllib2.install_opener(opener)
	data,headers=encode.encode_multipart(fields={'media_id':media_id,'req_token':request_token(auth_token,str(int(time.time()))),'timestamp':str(int(time.time())),'type':"0",'username':username,'zipped':"0"}, files={'data':{'filename':'data','content':data2}}, boundary='Boundary+0xAbCdEfGbOuNdArY')
	#m=MultipartEncoder(fields={'username':username,'timestamp':str(int(time.time())),'req_token':request_token(auth_token,str(int(time.time()))),'media_id':media_id,'type':"0",'zipped':"0",'data':data})
	#encode.post_multipart(API_URL, 'bq/upload', [('username',username),('timestamp',str(int(time.time()))),('req_token',request_token(auth_token,str(int(time.time())))),('media_id',media_id),('type',"0"),('zipped',"0")], [('file','data','data2')])

	headers['User-agent']= 'Snapchat/6.1.2 (iPhone5,1; iOS 7.1; gzip)'
	headers['Proxy-Connection']='keep-alive'
	#headers['Content-Type']='application/json'
	r = requests.post(API_URL+'bq/upload', data=data, headers=headers)
	# r=requests.post(API_URL+'bq/upload',data=m,headers=HEADERS)
	recipientstring=''
	for friend in listoffriends:
		recipientstring+=(friend+',')
	recipientstring=recipientstring[0:-1]

	params={'username':username,'timestamp':str(int(time.time())),'country_code':'US','req_token':request_token(auth_token,str(int(time.time()))),'media_id':media_id,'zipped':"0",'time':length,'recipient':recipientstring}
	r=requests.post(API_URL+'bq/send',data=params,headers=HEADERS)
	return r

def captchaSolver(imagezip):
	tempdir=tempfile.mkdtemp(dir=APP_STATIC)
	imagezip.extractall(tempdir)
	img1 = cv2.imread('ghost.png')
	sift = cv2.SIFT()
	kp1, des1 = sift.detectAndCompute(img1,None)
	averageDistance=[]
	for i in range(0,9):
		img2=cv2.imread(os.path.join(tempdir,'image'+str(i)+'.png'))
		kp2, des2 = sift.detectAndCompute(img2,None)
		matcher = cv2.FlannBasedMatcher({'algorithm':0,'trees':5},{'checks':50})
		matches = flann.knnMatch(des1,des2,k=2)
		a=sorted(map(lambda x: x.distance,sum(matches,[])))
		b=a[:10]
		averageDistance.append(sum(b)/float(len(b)))
	shutil.rmtree(tempdir)
	return ''.join(['1' if x else '0' for x in [distance<225 for distance in averageDistance]])