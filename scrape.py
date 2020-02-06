import requests
from bs4 import BeautifulSoup
import pandas as pd 
import sqlite3
from sqlite3 import Error
import csv

#TODO adding updated articles to the database without duplicates -  gen hashes for body strings

usernames = []
articleTitles = []
timesPosted = []

def create_table(cur):
    """
    Create the articles table in the database 
    """
    try:
        cur.execute('create table if not exists articles (id integer primary key, title, username, time_posted)')
    except Error as e:
        print(e)

def create_connection(db_file):
    """ 
    Create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        # conn represents the database
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        create_table(cur)
    except Error as e:
        print(e)

    return conn

def insert_article(conn, article):
    """
    Insert a new article into the articles table
    :param conn:
    :param article:
    :return: article id
    """
    cur = conn.cursor()
    cur.execute('insert into articles(title, username, time_posted) values(?,?,?)', article)
  
def scrape_articles():
    url = 'https://www.allkpop.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    startBlock = soup.findAll('div', attrs={'class': 'home_left width73'})[0]

    for a in startBlock.findAll('article', attrs={'class': 'list'}):
   
        if len(a.findAll('div', attrs={'class':'title'})) != 0:
            title = a.findAll('div', attrs={'class':'title'})[0]
    
        if len(a.findAll('div', attrs={'class':'info'})) != 0:
            user = a.findAll('div', attrs={'class':'info'})[0]
   
        extractedTitle = title.find('a', href=True, attrs={'class': 'h_a_i'})
        extractedUser = user.find('span', attrs={'class': 'akp_display_name author'})
        extractedTime = user.find('span', attrs={'class': 'realtime'})

        articleTitles.append(extractedTitle.text)
        usernames.append(extractedUser.text)
        timesPosted.append(extractedTime.text)

def main():
    scrape_articles()
  
    database = r'articles.db'

    # Create a database connection
    conn = create_connection(database)
    with conn:
        for i in range(len(articleTitles)):
            article = (articleTitles[i], usernames[i], timesPosted[i])
            insert_article(conn, article)

main()


