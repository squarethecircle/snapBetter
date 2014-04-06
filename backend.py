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
import encode
import urllib2
# import httplib2
from appdb import models
from appdb import db
from urlgrabber.keepalive import HTTPHandler
import sha
 
APP_STATIC='static/'
API_URL='https://feelinsonice-hrd.appspot.com/'
AES_KEY='M02cnQ51Ji97vwT4'
STATIC_TOKEN='m198sOkJEn37DjqZ32lpRu76xmw288xSQ9'
HEADERS={'User-agent': 'Snapchat/6.1.2 (iPhone5,1; iOS 7.1; gzip)'}
SS_USERNAME='secret_snapta'
SS_PASSWORD='3stacksqSort'

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
	queryuser=models.User.query.filter_by(username=username).first()
	if queryuser==None:
		newuser=models.User(username=username,password=password)
		db.session.add(newuser)
		db.session.commit()
		queryuser=newuser
	elif (queryuser.token!=None):
		r=update(username, queryuser.token)
		if (r!=False):
			return r
	params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'username':username,'password':password}
	r=requests.post(API_URL+'bq/login',data=params,headers=HEADERS)
	if (r.json().get('logged')==False):
		return False
	queryuser.token=r.json().get('auth_token')
	db.session.commit()
	return r.json()

def secret_snapta():

	r=login(SS_USERNAME,SS_PASSWORD)
	while (True):
		snaps = []
		snapids = unopenedIds(SS_USERNAME,r.get('auth_token'))
		if snapids:
			for snapdata in snapids:
				img=fetchSnap(SS_USERNAME,r.get('auth_token'), snapdata[0])
				if img:
					if not os.path.exists(APP_STATIC + "img/snaps/" + snapdata[0] + ".jpg"):
						f = open(APP_STATIC + "img/snaps/" + snapdata[0] + ".jpg", "w")
						f.write(img)
						f.close()
						newsnap=models.Snap(sentfrom=snapdata[1],sentto='secret_snapta',file=snapdata[0],timesent=int(snapdata[2]/1000))
						db.session.add(newsnap)
						db.session.commit()
				snaptosend = models.Snap.query.filter(models.Snap.sentfrom == snapdata[1]).first()
				if (snaptosend != None):
					filetosend = open(APP_STATIC + "img/snaps/" + snaptosend.file + ".jpg")
					sendSnap(SS_USERNAME,r.get('auth_token'), filetosend.read(),[snapdata[1]], 9)
					filetosend.close()
					os.remove(APP_STATIC + "img/snaps/" + snaptosend.file + ".jpg")
					db.session.delete(snaptosend)
					db.session.commit()
		time.sleep(5)


def update(username,auth_token):
	params={'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'username':username}
	r=requests.post(API_URL+'/bq/updates',data=params,headers=HEADERS)
	if r.status_code == 200:
		return r.json()
	else:
		return False

def encrypt_image(s):
	if s:
		s =s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
		cipher = AES.new(AES_KEY, AES.MODE_ECB, "")
		return cipher.encrypt(s)
	else:
		return False

def decrypt_image(s):
	if s:
		cipher = AES.new(AES_KEY, AES.MODE_ECB, "")
		return cipher.decrypt(s)
	else:
		return False
 
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
	if r.status_code == 200:
		return r.json()
	else:
		return False

def verifyCode(username,auth_token,code):
	params={'username':username,'action':'verifyPhoneNumber','code':code,'req_token':request_token(auth_token,int(time.time())),'timestamp':timestamp}
	r=requests.post(API_URL+'ph/settings',data=params,headers=HEADERS)
	if r.status_code == 200:
		return r.json()
	else:
		return False

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
	if r.status_code == 200:
		return r.content
	else:
		return False

#fetches IDs of unopened snaps
def unopenedIds(username, auth_token):
	r = update(username, auth_token)
	if r:
		unseen = []
		for snap in r['snaps']:
			if 't' in snap:
				if snap['t'] > 0:
					if snap['m'] == 0:
						unseen.append([snap['id'],snap['sn'],int(snap['sts'])])
		return unseen
	else:
		return False

#fetches all snaps and saved unsaved ones and writes them to the db
def updateSaveNewFSnaps(username, auth_token):
	fsnaps = []
	snapids = unopenedIds(username, auth_token)
	if snapids:
		for snapdata in snapids:
			#write to db
			newfsnap=models.FSnap(sentfrom=snapdata[1],sentto=username,file=snapdata[0],timesent=snapdata[2])
			db.session.add(newfsnap)
			db.session.commit()
			fsnaps.append(newfsnap)
			img=decrypt_image(fetchSnap(username, auth_token, snapdata[0]))
			if not os.path.exists(APP_STATIC + "img/fsnaps/" + snapdata[0] + ".jpg"):
				f = open(APP_STATIC + "img/fsnaps/" + snapdata[0] + ".jpg", "w")
				f.write(img)
				f.close()
		return fsnaps
	else:
		return False

#delete directory of fsnaps after logout
def deleteFSnapDir(username):
	fsnaps = models.FSnap.query.all()
	for fsnap in fsnaps:
		if os.path.exists(APP_STATIC + "img/fsnaps/" + fsnap.file + ".jpg"):
			os.remove(APP_STATIC + "img/fsnaps/" + fsnap.file + ".jpg")
		db.session.delete(fsnap)
		db.session.commit()
	


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