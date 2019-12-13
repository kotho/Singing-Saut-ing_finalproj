import requests
import json
import unittest
import os
import sqlite3
import re


def read_cache(CACHE_FNAME):
    """
    This function reads from the JSON cache file and returns a dictionary from the cache data. 
    If the file doesn’t exist, it returns an empty dictionary.
    """
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding='utf-8') # Try to read the data from the file
        cache_contents = cache_file.read()  # If it's there, get it into a string
        CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
        cache_file.close() # Close the file, we're good, we got the data in a dictionary.
    except:
        CACHE_DICTION = {}
    return CACHE_DICTION


def write_cache(cache_file, cache_dict):
    """
    This function encodes the cache dictionary (cache_dict) into JSON format and
    writes the contents in the cache file (cache_file) to save the search results.
    """
    CACHE_FNAME = cache_file
    dumped = json.dumps(cache_dict)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped)
    fw.close() # Close the open file


def get_random_with_caching():
    shit_list = [52929, 52914, 52840, 52832, 52966, 52954, 52852, 52867, 52915, 52780, 52897, 52893, 52894, 52984, 52802, 52848, 52819, 52864, 52837, 52833, 52889, 52814, 52909, 52807, 52767, 52891, 52934, 52795, 52841, 52830, 52906, 52821, 52805, 52782, 52876, 52930, 52783, 52836, 52806, 52863, 52866, 52957, 52788, 52769, 52903, 52787, 52808, 52843, 52880, 52858, 52810, 52932, 52921, 52809, 52811, 52786, 52817, 52931, 52882, 52912, 52926, 52845, 52828, 52917, 52871]
    base_url = "https://www.themealdb.com/api/json/v1/1/random.php"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "cache_mealdb.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)

    try:
        r = requests.get(base_url)
        data = r.text
        dict_list = json.loads(data)
        meh_dict = dict_list['meals'][0]
        ids = meh_dict['idMeal']
        if str(ids) in CACHE_DICTION.keys():
            print("Already exists in mealdb")
            return 1
        else:
            CACHE_DICTION[ids] = meh_dict
            if int(ids) not in shit_list:
                print("Adding to mealdb")
                write_cache(CACHE_FNAME, CACHE_DICTION)
                return ids
            else:
                return 1
    except:
        Print(exception)

def setup_db(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def find_time(meal):
    total = 0
    pattern = '(\d+)\smin'
    matches = re.findall(pattern, meal['strInstructions'])
    for item in matches:
        total = total + int(item)

    pattern = '(\d+)\shour'
    matches = re.findall(pattern, meal['strInstructions'])
    for item in matches:
        total = total + int(item)*60

    pattern = '(\d+)\shr'
    matches = re.findall(pattern, meal['strInstructions'])
    for item in matches:
        total = total + int(item)*60

    return total

def find_ingredients(meal):
    total = 0
    for i in range(1, 21):
        try:
            if len(meal['strIngredient{}'.format(i)]) > 0:
                total = total + 1
        except:
            continue
    return total

def create_mealtable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Meals(id INTEGER PRIMARY KEY, name TEXT UNIQUE, area TEXT, category TEXT, time INTEGER, ingredients INTEGER)')
    conn.commit()

def create_ingredientstable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Meals(id INTEGER PRIMARY KEY, name TEXT UNIQUE, area TEXT, category TEXT, time INTEGER, ingredients INTEGER)')
    conn.commit()

def update_db(CACHE_FNAME, cur, conn):
    meals = read_cache(CACHE_FNAME)
    for meal in meals.values():
        _id = int(meal['idMeal'])
        _name = meal['strMeal']
        _area = meal['strArea']
        _category = meal['strCategory']
        _time = find_time(meal)
        if _time == 0:
            _time = 20
        _ingredients = find_ingredients(meal)
        try:
            cur.execute('INSERT INTO Meals (id, name, area, category, time, ingredients) VALUES (?, ?, ?, ?, ?, ?)', (_id, _name, _area, _category, _time, _ingredients,))
        except:
            continue
    conn.commit()

def get_edamam(ids):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "cache_edamam.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)

    app_id = '75190b61'
    app_key = 'cb64e55cf0fa35409508ac478a8e08db'

    # app_id = '8da48df3'
    # app_key = 'b7fe240a25fd95dbd10a12ef715ae9df'

    # app_id = '3c7034c0'
    # app_key = '41a990c1d1ed02007ad4f6b4fec5f466'

    if str(ids) in CACHE_DICTION.keys():
            print("Already exists in Edamam")  
    else:
        try:
            url = "https://api.edamam.com/api/nutrition-details?app_id={}&app_key={}".format(app_id, app_key)
            payload = open('jason.json')
            headers = {'Content-Type': 'application/json'}
            r = requests.post(url, data=payload, headers=headers)
            data = r.text
            dict_list = json.loads(data)
            
            CACHE_DICTION[ids] = dict_list
            print("Adding to Edamam")
            write_cache(CACHE_FNAME, CACHE_DICTION)
        except:
            print("Edamam Exception")

def create_json(ids):
    base_url = "https://www.themealdb.com/api/json/v1/1/lookup.php?i={}".format(ids)
    print(ids)
    r = requests.get(base_url)
    data = r.text
    dict_list = json.loads(data)
    actual_dict = dict_list['meals'][0]
    ingredients = []
    name = actual_dict['strMeal']
    for i in range(1, 21):
        try:
            if len(actual_dict['strIngredient{}'.format(i)]) > 0:
                ingredients.append(actual_dict.get('strMeasure{}'.format(i)) + " " + actual_dict.get('strIngredient{}'.format(i)))
        except:
            continue
    jason_prep = {}
    jason_prep['title'] = name
    jason_prep['ingr'] = ingredients
    with open('jason.json', 'w', encoding='utf-8') as f:
        json.dump(jason_prep, f, ensure_ascii=False, indent=4)

def create_healthtable(cur, conn):
    cur.execute('DROP TABLE IF EXISTS Health')
    cur.execute('CREATE TABLE Health(id INTEGER PRIMARY KEY UNIQUE, servings REAL, calories REAL, weight REAL, label TEXT)')
    conn.commit()

def update_health(CACHE_FNAME, cur, conn):
    health = read_cache(CACHE_FNAME)
    for meal in health.items():
        _id = int(meal[0])
        health = meal[1]
        _servings = health['yield']
        _calories = health['calories']
        _weight = health['totalWeight']
        label_list = []
        for label in health['dietLabels']:
            cur.execute('SELECT id FROM Diets WHERE title like "{}"'.format(label))
            for row in cur:
                label_list.append(row[0])
        _labels = str(label_list).strip('[]')
        try:
            cur.execute('INSERT INTO Health (id, servings, calories, weight, label) VALUES (?, ?, ?, ?, ?)', (_id, _servings, _calories, _weight, _labels))
        except:
            continue
    conn.commit()

def create_diettable(CACHE_FNAME, cur, conn):
    label_dict = read_cache(CACHE_FNAME)
    label_list = []
    for meal in label_dict.values():
        diet_labels = meal['dietLabels']
        for diet in diet_labels:
            if diet not in label_list:
                label_list.append(diet)

    cur.execute("DROP TABLE IF EXISTS Diets")
    cur.execute("CREATE TABLE Diets (id INTEGER PRIMARY KEY, title TEXT)")
    for i in range(len(label_list)):
        cur.execute("INSERT INTO Diets (id,title) VALUES (?,?)",(i,label_list[i]))
    conn.commit()

def calc_full(cur, conn):
    file_ = open('size.txt', 'w')
    file_.write('Percent Daily\n')
    file_ = open('size.txt', 'a')
    cur.execute("SELECT id, name, calories, servings FROM Joined")
    for row in cur:
        ids = int(row[0])
        name = row[1]
        calories = row[2]
        servings = row[3]
        out = calories/servings/2000 * 100
        file_.write(str(ids) + " - " + name + " : " + str(round(out, 1)) + "%\n")
    file_.close()

def calc_dif(cur, conn):
    file_ = open('meal_dif.txt', 'w')
    file_.write('Meal Difficulty\n')
    file_ = open('meal_dif.txt', 'a')
    cur.execute("SELECT id, name, time, ingredients FROM Meals")
    for row in cur:
        ids = int(row[0])
        name = row[1]
        time = int(row[2])
        ingr = int(row[3])
        ingr_dif = ingr / 2
        if time < 10:
            time_dif = 1
        if time < 20:
            time_dif = 2
        elif time < 30:
            time_dif = 3
        elif time < 40:
            time_dif = 4
        elif time < 50:
            time_dif = 5
        elif time < 60:
            time_dif = 6
        elif time < 80:
            time_dif = 7
        elif time < 100:
            time_dif = 8
        elif time < 120:
            time_dif = 9
        else:
            time_dif = 10
        dif = (ingr_dif + time_dif)/2
        file_.write(str(ids) + " - " + name + " : " + str(dif) + "\n")
    file_.close()

def join_mealed(cur, conn):
    cur.execute('Create TABLE IF NOT EXISTS Joined AS SELECT Meals.id, name, area, category, time, ingredients, Health.servings, Health.calories, Health.weight, Health.label FROM Meals JOIN Health on Health.id = Meals.id')
    conn.commit()

def main():
    cur, conn = setup_db('singing&sautéing.db')
    create_mealtable(cur, conn)
    create_healthtable(cur, conn)

    # for i in range(20):
    #     ids = get_random_with_caching()
    #     if ids != 1:
    #         create_json(ids)
    #         get_edamam(ids)
    #     else:
    #         i = i - 1

    update_db('cache_mealdb.json', cur, conn)
    create_diettable('cache_edamam.json', cur, conn)
    update_health('cache_edamam.json', cur, conn)
    join_mealed(cur, conn)
    calc_dif(cur, conn)
    calc_full(cur, conn)


if __name__ == "__main__":
    main()