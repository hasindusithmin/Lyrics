import json
from main import app
from random import randint
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root():
    response = client.get('/')
    assert response.status_code == 200

def test_find_all_singers():
    response = client.get('/singers')
    assert response.status_code == 200
    res_body = response.json()
    file = open('singers.json','r')
    data = json.load(file)
    assert len(res_body) == len(data)
    for i in range(len(res_body)):
        assert data[i]['name'] == res_body[i]['name']
        assert data[i]['key'] == res_body[i]['key']


def test_find_singers_by_valid_letter():
    letter = 'a'
    res = client.get(f'/singersbyletter/{letter}')
    assert res.status_code == 200
    res_body = res.json()
    random_obj = res_body[randint(0,len(res_body)-1)]
    obj_keys = random_obj.keys()
    assert 'name' in obj_keys
    assert 'key' in obj_keys

def test_find_singers_by_invalid_letter():
    letter = '5'
    res = client.get(f'/singersbyletter/{letter}')
    assert res.status_code == 400
    res_body = res.json()
    assert res_body['detail'] == f"{letter} isn't alphabet"

def test_not_exists_singers_by_valid_letter():
    letter = 'z'
    res = client.get(f'/singersbyletter/{letter}')
    assert res.status_code == 404
    res_body = res.json()
    assert res_body['detail'] == "singers not found"

def test_find_songs_by_singer_valid_key():
    valid_key = "2017/11/angeline-gunathilake"
    res = client.get(f'/songsbysinger?key={valid_key}')
    assert res.status_code == 200
    res_body = res.json()
    random_obj = res_body[randint(0,len(res_body)-1)]
    obj_keys = random_obj.keys()
    assert 'name' in obj_keys
    assert 'key' in obj_keys

def test_find_songs_by_singer_invalid_key():
    invalid_key = "xxxxxxxxxxxxxxx"
    res = client.get(f'/songsbysinger?key={invalid_key}')
    assert res.status_code == 400
    res_body = res.json()
    assert res_body['detail'] == 'invaild key'


def test_find_lyrics_by_song_valid_key():
    key = '2017/10/atha-wanniye-guru-gei-para-asa'
    res = client.get(f'/lyrics?key={key}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'image/png'

def test_find_lyrics_by_song_invalid_key():
    key = 'xxxxxxxxxxxxxx'
    res = client.get(f'/lyrics?key={key}')
    assert res.status_code == 404
    assert res.json()['detail'] == 'lyrics not found'