import requests
import os
import json
import base64
import sqlite3
#import pyyaml

def authorize():

    client_id = "b5a6f1699aa3453d88201d2c708a94a9"
    client_secret = "7b38175d842b4599866a2b1be5437a02"

    auth_str = '{}:{}'.format(client_id, client_secret)
    b64_auth = base64.urlsafe_b64encode(auth_str.encode()).decode()

    headers = {
        'Authorization': 'Basic {}'.format(b64_auth),
    }

    data = {
        'grant_type': 'client_credentials'
    }

    url = "https://accounts.spotify.com/api/token"

    auth = requests.post(url, headers=headers, data=data)
    
    data = str(auth.text)    
    dict_list = json.loads(data) # decoding JSON file

    return(dict_list['access_token'])




def get_playlists_by_country(access_token, country):

    access_t = access_token
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(access_t)
    }

    params = {
        ('country', country),
        ('limit', '1'),
        ('offset', '5')
    }

    response = requests.get('https://api.spotify.com/v1/browse/categories/dinner/playlists', headers=headers, params=params)

    dic = json.loads(str(response.text)) # decoding JSON file

    id_ = dic['playlists']['items'][0]['id']
    name = dic['playlists']['items'][0]['name']
    desc = dic['playlists']['items'][0]['description']
    playlist_img = dic['playlists']['items'][0]['images'][0]['url']

    return((str(id_), str(name), str(desc), str(playlist_img)))




def get_playlist_tracks(api_token, playlist_id, country):
    
    access_t = api_token

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(access_t)
    }

    url = 'https://api.spotify.com/v1/playlists/{}/tracks?market={}&limit=20'.format(playlist_id, country)
    response = requests.get(url, headers=headers).json()

    new = {}

    for item in response['items']:
        dic = item['track']
        new[dic['id']] = dic
    
    return new



def caching(cache_file, cache_dict):
    pretty = json.dumps(cache_dict)
    f = open(cache_file, 'w')
    f.write(pretty)
    f.close()


def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path)
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createTable1(cur, conn):
    #cur.execute('DROP TABLE IF EXISTS Tracks')
    cur.execute('CREATE TABLE IF NOT EXISTS Tracks(id TEXT, country TEXT, name TEXT, artist TEXT, duration INTEGER, preview INTEGER, popularity TEXT)')

    conn.commit()


def createTable2(cur, conn):
    #cur.execute('DROP TABLE IF EXISTS SongTimes')
    cur.execute('CREATE TABLE IF NOT EXISTS SongTimes(id TEXT, country TEXT, duration FLOAT)')

    conn.commit()


def createTable3(cur, conn):
    #cur.execute('DROP TABLE IF EXISTS Popularity')
    cur.execute('CREATE TABLE IF NOT EXISTS Popularity(country TEXT, popularity INTEGER)')


def setUpSpotifyTable1(data, country, cur, conn):
    cur.execute('SELECT country FROM Tracks')
    for row in cur:
        if row[0] == country:
            return

    for track in data.values():
        _id = track['id']
        _country = country
        _name = track['name']
        _artist = track['artists'][0]['name']
        _duration = track['duration_ms']
        _preview = track['preview_url']
        _popularity = track['popularity']
        cur.execute('INSERT INTO Tracks (id, country, name, artist, duration, preview, popularity) VALUES (?, ?, ?, ?, ?, ?, ?)', 
            (_id, _country, _name, _artist, _duration, _preview, _popularity))

    conn.commit()


def setUpSpotifyTable2(data, country, cur, conn):
    spot_data_file = open("spot_data_duration.txt", "w")
    spot_data_file.write("DURATION CONVERSION\n\n")

    cur.execute('SELECT country FROM SongTimes')
    for row in cur:
        if row[0] == country:
            return


    for track in data.values():
        _id = track['id']
        _country = country
        _duration = track['duration_ms'] / 60000
        cur.execute('INSERT INTO SongTimes (id, country, duration) VALUES (?, ?, ?)', 
            (_id, _country, _duration))

    conn.commit()

    cur.execute('SELECT id, name FROM Tracks')

    id_name = {}

    for row in cur:
        id_name[row[0]] = row[1]

    cur.execute('SELECT id, country, duration FROM SongTimes')
    for row in cur:
        for key in id_name.keys():
            if key == row[0]:
                line = str(id_name[key]) + " (" + str(row[1]) + "): " + str(round(row[2]*60000, 2)) + " milliseconds to " + str(round(row[2], 2)) + " minutes\n"
                spot_data_file.write(line)

    spot_data_file.close()



def setUpSpotifyTable3(country, cur, conn):
    spot_data_file = open("spot_data_popularity.txt", "w")
    spot_data_file.write("POPULARITY AVERAGE PER PLAYLIST\n\n")

    cur.execute('SELECT country FROM Popularity')
    for row in cur:
        if row[0] == country:
            return

    cur.execute('SELECT country, popularity FROM Tracks')

    pop_count = []
    p = {}
    c = {}

    for row in cur:
        if country == row[0]:
            p[str(row[0])] = p.get(str(row[0]), int(row[1])) + int(row[1])
            c[str(row[0])] = c.get(str(row[0]), 1) + 1

    for key in p.keys():
        for key2 in c.keys():
            if key == key2:
                pop_count.append((key, p[key]/c[key]))

    _country = country
    _popularity = pop_count[0][1]
    cur.execute('INSERT INTO Popularity (country, popularity) VALUES (?, ?)', 
        (_country, _popularity))

    conn.commit()

    cur.execute('SELECT country, popularity FROM Popularity')
    for row in cur:
        spot_data_file.write(str(row[0]) + " playlist has an average popularity of " + str(round(row[1], 2)) + "/100\n")

    spot_data_file.close()


def main():

    api_key = authorize()
    country = 'VN'
    gpc = get_playlists_by_country(api_key, country)
    gpt = get_playlist_tracks(api_key, gpc[0], country)
    #for i in range(15):
    caching('cache_spotify.json', gpt)

    cur, conn = setUpDatabase("singing&sautéing.db")

    createTable1(cur, conn)
    data = readDataFromFile("cache_spotify.json")
    setUpSpotifyTable1(data, country, cur, conn)

    createTable2(cur, conn)
    setUpSpotifyTable2(data, country, cur, conn)

    createTable3(cur, conn)
    setUpSpotifyTable3(country, cur, conn)



if __name__ == "__main__":
    main()