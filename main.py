import io
import json
import string
import requests
from PIL import Image
from bs4 import BeautifulSoup
from fastapi import FastAPI,HTTPException,status
from fastapi.responses import StreamingResponse,FileResponse,RedirectResponse,JSONResponse
from fastapi.middleware.cors import CORSMiddleware

description = """
### Test Report [click](/report)

![screencast](https://i.ibb.co/BrWMFfS/Screencast.gif)

"""
app = FastAPI(
    title="Lyrics API",
    description=description,
    version="0.2.0",
    contact={
        "name": "find me on Linkedin",
        "url": "https://www.linkedin.com/in/hasindu-sithmin-9a1a12209/",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return RedirectResponse('/docs')

@app.get('/report',tags=['See test report'],description='## [Link](https://sinhalalyrics.deta.dev/report)')
def root():
    return FileResponse('report.html')

@app.get('/singers',tags=['ALL singers'],description="## [Link](https://sinhalalyrics.deta.dev/singers)")
def find_all_singers():
    with open('__singers.json','r') as fp:
        return json.load(fp)
    
@app.get('/songs',tags=['ALL songs'],description="## [Link](https://sinhalalyrics.deta.dev/songs)")
def find_all_songs():
    with open('__songs.json','r') as songs:
        return json.load(songs)

@app.get('/singersbyletter/{letter}',tags=['Get singers by alphabet'],description="### letter parameter must be an alphabet letter")
async def find_singers_by_letter(letter:str):
    letter = letter.lower()
    alphabet = [char for char in string.ascii_lowercase]
    if letter not in alphabet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{letter} isn't alphabet")
    url = f"https://www.sinhalalyricspedia.com/2017/10/sinhala-artists-{letter}.html"
    res = requests.get(url,headers={'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
    soup = BeautifulSoup(res.content,'lxml')
    try:
        ul = soup.find('ul',class_='list-group')
        return [{'name':li.find('a').text.split('(')[0].strip(),'key':li.find('a').get('href')[1:].replace('.html','')} for li in ul.find_all('li',class_='list-group-item justify-content-between')]
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='singers not found')
  
@app.get('/songsbysinger',tags=['Get songs by singer'],description="query **singer** must be a valid")
async def find_songs_by_singer(singer:str):
    singersobj,singers = {},[]
    with open('_singers.json','r') as fp:
        singersobj = json.load(fp)
        singers = list(singersobj.keys())
    if singer not in singers:
        raise HTTPException(status_code=404,detail=f"singer ('{singer}') not found")
    url = f'https://www.sinhalalyricspedia.com/{singersobj[singer]}.html'
    res = requests.get(url,headers={'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
    if res.status_code == 404:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='invaild key')
    soup = BeautifulSoup(res.content,'lxml')
    songs = soup.find('ul',class_='list-group').find_all('li',class_='list-group-item')
    songs.pop(0)
    obj = {}
    for song in songs:
        name = song.text.split('(')[0].strip()
        key = name.replace(' ','-').lower()
        obj[name] = key
    return obj
    

@app.get('/lyrics',tags=['Get lyrics by song'],description="query **song** must be a valid")
async def find_lyrics_by_song(song:str):
    try:
        songsobj,songs = {},[]
        with open('_songs.json','r') as fp:
            songsobj = json.load(fp)
            songs = list(songsobj.keys())
        if song not in songs:
            return JSONResponse({'detail':f"songs ('{song}') not found"},status_code=404)
        url = f'https://www.sinhalalyricspedia.com/{songsobj[song]}.html'
        res = requests.get(url,headers={'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})
        soup = BeautifulSoup(res.content,'lxml')
        image_url = soup.find('img',{'id':'lyricsImage'}).get('src')
        r = requests.get(image_url,stream=True)
        r.raw.decode_content = True
        image = Image.open(r.raw)
        width, height = image.size
        crop_image = image.crop((0,0,width,height-60))
        buffer = io.BytesIO()
        crop_image.save(buffer,format='PNG')
        buffer.seek(0)
        return StreamingResponse(buffer,media_type='image/png')
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='lyrics not found')
