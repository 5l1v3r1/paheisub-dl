import requests,os,sys,click,re,time
import logging
from tqdm import tqdm
from bs4 import BeautifulSoup as Bs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

__version="v0.1 (BETA)"

if len(sys.argv) > 1 and sys.argv[1] == '--debug':
	print("\033[93mMODE DEBUG: TRUE\033[97m".center(45))
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

ses=requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
ses.mount('http://', HTTPAdapter(max_retries=retries))
ses.mount('https://', HTTPAdapter(max_retries=retries))

############################################
def download(url,judul):
	r = ses.get(url, stream=True)
	total_size = int(r.headers.get('content-length', 0))
	print(f"\n# Downloading {judul}")
#	print(f"['{url}']")
	block_size = 1024
	t=tqdm(total=total_size, unit='iB', unit_scale=True)
	with open(f'result/{judul.replace("/",",")}','wb') as f:
		for data in r.iter_content(chunk_size=block_size):
			if data:
				t.update(len(data))
				f.write(data)
	t.close()
	if total_size != 0 and t.n != total_size:
		print("\n[Warn] Download GAGAL")
		tan=input("[?] anda ingin melanjutkannya ke website (y/n) ")
		if tan.lower() == 'y':
			click.launch(url)
		else:
			sys.exit("okay bye bye:*")
###########################################

#subtitle downloader
def subdl(q):
	try:
		uli=[]
		sdl=[]
		req=ses.get('https://isubtitles.org/search?kwd='+q)
		bs=Bs(req.text, 'html.parser')
		hsl=bs.find_all('h3')

		n=1
		print("\n\t[ Result ]")
		for a in hsl:
			uli.append(a.find('a')['href'])
			print(f"{n}. {a.find('a').text}")
			n+=1
		cho=int(input("_> pilih: "))
		if cho <= 0:
			print("index out of ranges")
			return True

		req2=ses.get(f"https://isubtitles.org{uli[cho-1].replace('-subtitle','/indonesian-subtitles')}")
		bs2=Bs(req2.text, 'html.parser')

		sudl=bs2.find_all('td',{'data-title':'Download'})
		for a in sudl:
			sdl.append(a.find('a')['href'])
		mr=bs2.find_all('td',{'data-title':'Release / Movie'})
		cm=bs2.find_all('td',{'data-title':'Comment'})

		nn=1
		print("\n\t[ Result ]")
		for x,y in zip(mr,cm):
			print(f"{nn}. {x.text.strip()[:50]}\n# {y.text[:50]}")
			print("="*50)
			nn+=1
		ice=int(input("_> pilih: "))
		if ice <= 0:
			print("index out of ranges")
			return True

		download("https://isubtitles.org"+sdl[ice-1], x.text.strip()[:50]+"-subtitle.zip")
	except Exception as Er:
		print(Er)

#pahe.in downloader
info={
	'title':[],
	'resu':[]
}
def search(q):
	global pil
	req=ses.get("https://pahe.me/?s="+q)
	bs=Bs(req.text, 'html.parser')
	hsl=bs.find_all('h2',{'class':'post-box-title'})
	for x in hsl:
		info['title'].append((x.find('a')['href'], x.text.strip()))
	if len(info['title']) == 0:
		print("Tidak dapat menemukan judul film")
		return True
	
	c=1
	print("\n\t[ Result ]")
	for i in info['title']:
		print(f"{c}. {i[1]}")
		c+=1
	pil=int(input("_> pilih: "))
	if pil <= 0:
		print("index out of ranges")
		return True

	getres(info['title'][pil-1][0])

def getres(url):
	global lih
	mylist1=[]
	mylist2=[]
	req=ses.get(url)
	bs=Bs(req.text, 'html.parser')
	hsl=bs.find_all('div', {'class':'box-inner-block'})

	for y in hsl:
		ur=[i['href'] for i in y.find_all('a',{'class':'shortc-button small white '})]
		mylist1+=ur

	for y in hsl:
		ti=[b.text for b in y.find_all('b')]
		mylist2+=ti

	if len(mylist1)==0:
		for y in hsl:
			ur=[i['href'] for i in y.find_all('a',{'class':'shortc-button small white'})]
			mylist1+=ur
			if len(mylist1)==0:
				yahh=input(":( URL yang dapat kami bypass tidak tersedia\nApakah anda ingin mendownload di websitenya? (y/n) ")
				if yahh.lower() == 'y':
					click.launch(url)
				return True

	cc=1
	print("\n\t[ Resulution ]")
	for x, y in zip(mylist1, mylist2):
		info['resu'].append((x,y))
		print(f"{cc}. {y}")
		cc+=1
	lih=int(input("_> pilih: "))
	if lih <= 0:
		print("index out of ranges")
		return True

	try:
		bypass(info['resu'][lih-1][0])
	except:
		print("Gagal membypass :(")

def bypass(link):
	print(" *Bypassing please wait...")
	for _ in range(5):
		try:
			req=ses.post("https://nuubi.herokuapp.com/pahe/bypass", data={'url':link})
			url=re.findall(r"href='(.*?)'",req.text)[0]
		except Exception as er:
			print(f"Oops, {er}, mengulangi lagi...")
			time.sleep(3)
			continue
		else:
			break

	req2=ses.get(url)
	bs=Bs(req2.text, 'html.parser')
	url2=bs.find('a',{'class':'btn btn-primary btn-xs'})['href']
	
	reqs=ses.get(url2)
	link=re.findall("href='(.*?)'>Download ",reqs.text)[0]
	
	reqs_=ses.get(link)
	time.sleep(2)
	reqs2=ses.get(link)
	bs2=Bs(reqs2.text,'html.parser')
	dlink=bs2.find('a',{'title':'Download'})['href']

	try:
		download(dlink,f"{info['title'][pil-1][1]}{info['resu'][lih-1][0]}.mkv")
	except:
		yahh=input(":( Download GAGAL\nApakah anda ingin mendownload di websitenya? (y/n) ")
		if yahh.lower() == 'y':
			click.launch(url2)


if __name__ == '__main__':
	def c():
		try:
			os.system('clear')
		except:
			os.system('cls')
	try:
		os.mkdir('result')
	except: pass

	banner=f"""
	| Pahe.In dan Isubtitles.org DOWNLOADER |
			By Noobie
version = {__version}
		"""

	print(banner)
	tany=int(input("[1] Download Film\n[2] Download Subtitle\n_> pilih: "))
	if tany == 1:
		c()
		print(banner)
		que=input("[Film] Judul: ")
		search(que)
	elif tany == 2:
		c()
		print(banner)
		que=input("[Subs] Judul: ")
		subdl(que)
	else:
		sys.exit("?"*10000000)

	while True:
		pilihan="""
[?] Ingin mendownload lagi?
[J] iya, dengan judul yang beda
[R] iya, dengan resolusi yang beda
[S] iya, tapi download subtitle
[G] gak, gw mau nonton filmnya
"""
		tany=input(f"{pilihan}_> pilih: ")
		if tany.lower() == 'j':
			c()
			print(banner)
			info['title']=[]
			info['judul']=[]
			que=input("[Film] Judul: ")
			search(que)
		elif tany.lower() == 's':
			c()
			print(banner)
			que=input("[Subs] Judul: ")
			subdl(que)
		elif tany.lower() == 'r':
			co=1
			if not info['resu']:
				print("Riwayat resolusi tidak ada")
				continue
			for x in info['resu']:
				print(f"{co}. {x[1]}")
				co+=1
			lih2=int(input("_> pilih: "))
			lnk=info['resu'][lih2-1][0]
			info['resu']=""
			try:
				bypass(lnk)
			except:
				print("Gagal membypass :(")
		elif tany.lower() == 'g':
			print("Selamat menonton :)")
			break
		else:
			print("?"*100)
