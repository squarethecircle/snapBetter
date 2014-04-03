import requests
import hashlib
import json
import sys
import time
import os
import tempfile
import random
from config import APP_STATIC
from Crypto.Cipher import AES
import zipfile
import numpy as np
import cv2
import shutil
import uuid


API_URL='https://feelinsonice-hrd.appspot.com/'
AES_KEY='M02cnQ51Ji97vwT4'
STATIC_TOKEN='m198sOkJEn37DjqZ32lpRu76xmw288xSQ9'
HEADERS={'User-agent': 'Snapchat/6.1.2 (iPhone5,1; iOS 7.1; gzip)'}

def register(username, email, password, age, birthday):
params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'time_zone':'America/New_York','email':email,'password':password,'age':int(age),'birthday':birthday}
r=requests.post(API_URL+'bq/register',data=params,headers=HEADERS)
if (r.json().get('logged')==False):
	return r.json()
if (r.json().get('captcha')!=None):
	token=r.json().get('auth_token')
	params={'username':email,'timestamp':int(time.time()),'req_token':request_token(token,int(time.time()))}
	r=requests.post(API_URL+'bq/get_captcha',data=params,headers=HEADERS)
	cap_id_loc=r.headers.get('content-disposition').find('filename=')
	cap_id=r.headers.get('content-disposition')[cap_id_loc+9:-4]
	with tempfile.NamedTemporaryFile(dir=APP_STATIC) as f:
		f.write(r.content)
		imagezip=zipfile.ZipFile(f)
		result=captchaSolver(imagezip)
	params={'captcha_id':cap_id,'captcha_solution':result,'username':email,'timestamp':int(time.time()),'req_token':request_token(token,int(time.time()))}
	r=requests.post(API_URL+'bq/solve_captcha',data=params,headers=HEADERS)
	if (r.status_code!=200):
		return "Captcha Failed!"
token=r.json().get('token')
params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'email':email,'username':username}
r=requests.post(API_URL+'ph/registeru',data=params,headers=HEADERS)
if (r.json().get('logged')==False):
	return r.json()
return r.json()

def login(username,password):
	params={'timestamp':int(time.time()),'req_token':request_token(STATIC_TOKEN,int(time.time())),'username':username,'password':password}
	r=requests.post(API_URL+'bq/login',data=params,headers=HEADERS)
	if (r.json().get('logged')==False):
		return False
	return r.json()
def update(username,auth_token):
	params={'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'username':username}
	r=requests.post('')
def encrypt_image(filename):
	cipher = AES.new(AES_KEY, AES.MODE_ECB, "")
	newfile=tempfile.NamedTemporaryFile(dir=APP_STATIC)
	newfile.write(cipher.decrypt(f.read()))
	return newfile

def secretSanta():
	login('secretSnapta','3stacksqSort')

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

def verifyCode(username,auth_token,code):
	params={'username':username,'action':'verifyPhoneNumber','code':code,'req_token':request_token(auth_token,int(time.time())),'timestamp':timestamp}
	r=requests.post(API_URL+'ph/settings',data=params,headers=HEADERS)

def createGroup(username, listoffriends):
	dummyname=''.join(random.choice('0123456789ABCDEF') for i in range(10))
	dummyname=username+dummyname
	dummypassword=''.join(random.choice('012345') for i in range(5))+''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(5))+'A'
	gentime=random.random()*800409600
	gendate=time.gmtime(time)
	result=register(dummyname, dummyname+'@gmail.com', dummypassword, time.strftime("%x",date), int((time.time()-gentime)/31557600))
	if (!result) return False
	token=result.get('auth_token')	
	newgroup=models.Group(owner=models.User.query.filter_by(username=username).first().id,dummy_user=dummyname, dummy_password=dummypassword, dummy_token=token)
	db.session.add(newgroup)
	for i in listoffriends:
		newGroupMember=models.GroupMember(username=i,group.id=newgroup.id)
		db.session.add(newGroupMember)
	db.session.commit()

def sendSnap(username, auth_token, data, listoffriends, length):
	media_id=username.capitalize()+'~'+str(uuid.uuid1())
	params={'username':username,'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'media_id':media_id,'type':0,'data':data}
	r=requests.post(API_URL+'ph/upload',data=params,headers=HEADERS)
	recipientstring=''
	for friend in listoffriends:
		recipientstring+=(friend+',')
	recipientstring=recipientstring[-1]
	params={'username':username,'timestamp':int(time.time()),'req_token':request_token(auth_token,int(time.time())),'media_id':media_id,'zipped':"0",'time':length,'recipient':recipientstring}
	r=requests.post(API_URL+'ph/send',data=params,headers=HEADERS)
	return r.json()


	
def captchaSolver(imagezip):
tempdir=tempfile.mkdtemp(dir=APP_STATIC)
imagezip.extractall(tempdir)
img1 = cv2.imread('ghost.png')
img1b=cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
ret,img1t=cv2.threshold(img1b,244,255,cv2.THRESH_BINARY)
#img3 = cv2.imread('ghost2.png')
sift = cv2.SIFT()
kp1, des1 = sift.detectAndCompute(img1t,None)
#kp3, des3 = sift.detectAndCompute(img3,None)
retstuf = []
for i in range(0,9):
	print i
	#badhash=hashlib.md5(open(os.path.join(tempdir,'image'+str(i)+'.png')).read()).hexdigest()
	badhash=hashlib.md5(open('get_captcha 7/image'+str(i)+'.png').read()).hexdigest()
	if (badhash=='1b38a4b4e601ff1778f565f0de1fc2d1' or badhash=='7bfa3ac17754936bfa7014c0b1039d59' or badhash=='0c44560347318278697bcea811d7e964'):
		retstuf.append(1)
		continue
	#img2=cv2.imread(os.path.join(tempdir,'image'+str(i)+'.png'))
	img2=cv2.imread('get_captcha 7/image'+str(i)+'.png')
	img2b=cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
	ret,img2t=cv2.threshold(img2b,244,255,cv2.THRESH_BINARY)
	kp2, des2 = sift.detectAndCompute(img2t,None)
	matcher = cv2.FlannBasedMatcher({'algorithm':0,'trees':5},{'checks':50})
	#matcher2 = cv2.FlannBasedMatcher({'algorithm':0,'trees':5},{'checks':50})
	matches = matcher.knnMatch(des1,des2,k=1)
	#matches2 = matcher2.knnMatch(des3,des2,k=1)
	a=sorted(map(lambda x: x.distance,sum(matches,[])))
	b=a[:10]
	#c=sorted(map(lambda y: y.distance,sum(matches2,[])))
	#d=c[:10]
	if (b[0]<100):
		retstuf.append(1)
	else:
		retstuf.append(0)
shutil.rmtree(tempdir)
return ''.join(['1' if x else '0' for x in retstuf])
