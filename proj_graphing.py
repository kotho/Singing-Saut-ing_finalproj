import matplotlib.pyplot as plt
import sqlite3
import unittest
import os
import numpy as np

def connect_db(db_filename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_filename)
    cur = conn.cursor()
    return cur, conn


def get_popularity_dict(cur, conn):
    cur.execute('SELECT country, popularity FROM Popularity')

    c_pop = {}

    for row in cur:
        c_pop[row[0]] = row[1]

    return c_pop



def bar_popularity(c_pop):
    country = []
    popularity = []

    scp = sorted(c_pop.items())

    for tup in scp:
        country.append(tup[0])
        popularity.append(tup[1])

    fig, ax = plt.subplots()

    index = np.arange(len(country))
    ax.bar(index, popularity, color="gold")

    plt.xlabel("Country (by code)")
    plt.ylabel("Popularity (out of 100)")
    plt.title("Popularity of Playlists by Country")

    # Use these to make sure that your x axis labels fit on the page
    plt.xticks(index, country, rotation=90)
    plt.tight_layout()

    fig.savefig("popularity_by_country.png")

    plt.show()

    return scp



def create_regionstable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Regions(area TEXT, counts INTEGER)')
    cur.execute('INSERT INTO Regions SELECT area, count(*) FROM Meals GROUP BY area')
    conn.commit()



def barchart_restaurants_by_reg(cur, conn):
    cur.execute('SELECT area, count(*) FROM Meals GROUP BY area')
    plt.xlabel('Region')
    plt.ylabel('Number of Meals')
    plt.title('Number of Meals by Region')

    region = ['American', 'British', 'Canadian', 'Chinese', 'Dutch', 'Egyptian', 'French', 'Greek', 'Indian', 'Italian', 'Jamaican', 'Japanese', 'Kenyan', 'Mexican', 'Moroccan', 'Spanish', 'Thai', 'Tunisian', 'Turkish', 'Unknown', 'Vietnamese']
    count = [11, 24, 5, 5, 1, 1, 17, 1, 7, 10, 5, 3, 1, 3, 5, 2, 2, 3, 1, 1, 1]
    plt.bar(region, count, color='gold')
    plt.xticks(rotation=90)
    plt.tight_layout()
    
    plt.show()



def barchart_restaurants_by_cat(cur, conn):
    cur.execute('SELECT category, count(*) FROM Meals GROUP BY category')
    plt.xlabel('Category')
    plt.ylabel('Number of Meals')
    plt.title('Number of Meals by Category')
    region = ['Breakfast', 'Dessert', 'Miscellaneous', 'Pasta', 'Seafood', 'Side', 'Starter', 'Vegan', 'Vegetarian']
    count = [2, 25, 6, 3, 10, 7, 2, 2, 15]
    plt.bar(region, count, color='gold')
    plt.xticks(rotation=90)
    plt.tight_layout()
    
    plt.show()



def piechart_meals_by_cat(cur, conn):
    cur.execute('SELECT title, count(*) FROM Diets GROUP BY title')
    plt.title('Number of Meals by Health Label')
    diet = 'Balanced', 'Low Carb', 'Low Fat'
    count = [5, 19, 3]
    colors = ['gold', 'red', 'blue']
    plt.pie(count, labels=diet, colors=colors)

    plt.show()



def main():
    cur, conn = connect_db('singing&sautéing.db')
    c_pop = get_popularity_dict(cur, conn)
    bar_popularity(c_pop)
    barchart_restaurants_by_reg(cur, conn)
    barchart_restaurants_by_cat(cur, conn)
    piechart_meals_by_cat(cur, conn)


if __name__ == "__main__":
    main()
