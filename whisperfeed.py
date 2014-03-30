import requests

def send(url, puid, wid):
	r = requests.get(url + '?puid=' + puid)
	if r.status_code == 200:
		return r.content
	else:
		return None


def main():
	f = open('whisperlog.txt', 'r')
	sentids = f.readlines()
	f.close()

	f = open('whisperlog.txt', 'a')

	limit = 100
	while (True):
		popular = 'http://prod.whisper.sh/whispers/popular?limit='+str(limit);
		r = requests.get(popular)
		json = r.json()['popular']

		for idx,whisper in enumerate(json):
			if idx < limit - 100:
				continue
			if not whisper['wid']+'\n' in sentids:
				resp =  send(whisper['url'], whisper['puid'], whisper['wid']);
				if resp:
					f.write(whisper['wid']+'\n')
					f.close()
					return resp
				else:
					return None
		limit+=100


if __name__ == "__main__":
    main()
