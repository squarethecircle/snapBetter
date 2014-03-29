import requests

def send(url, puid, wid):
	r = requests.get(url + '?puid=' + puid)
	if r.status_code == 200:
		f = open('static/img/whispers/' + str(wid), 'w')
		return r.content
	else:
		return None


def main():
	f = open('whisperlog.txt', 'r')
	sentids = f.readlines()
	f.close()

	f = open('whisperlog.txt', 'a')

	popular = 'http://prod.whisper.sh/whispers/popular';
	r = requests.get(popular)
	json = r.json()['popular']

	for whisper in json:
		if not whisper['wid']+'\n' in sentids:
			resp =  send(whisper['url'], whisper['puid'], whisper['wid']);
			if resp:
				f.write(whisper['wid']+'\n')
				f.close()
				return resp
			else:
				return None

	popular = 'http://prod.whisper.sh/whispers/latest';
	r = requests.get(popular)
	json = r.json['latest']
	for whisper in json:
		if not whisper['wid']+'\n' in sentids:
			resp =  send(whisper['url'], whisper['puid'], whisper['wid']);
			if resp:
				f.write(whisper['wid']+'\n')
				f.close()
				return resp
			else:
				return None

if __name__ == "__main__":
    main()
