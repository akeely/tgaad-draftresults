#!/usr/bin/python

import MySQLdb
import json
import os
from jinja2 import Environment, FileSystemLoader

def write_league_file(name, cursor):
    cursor.execute("""
        SELECT p.name, pw.team, p.position, pw.price, pw.time
        FROM players_won pw
        JOIN players p
          ON p.playerid=pw.name
        WHERE league = '{0}'
    """.format(name))

    players = cursor.fetchall()

    data = {'data': players}

    data_dir = "data/results"
    data_file = os.path.join(data_dir, "{0}.json".format(name))

    with open(data_file, 'w') as outfile:
        json.dump(data, outfile)

def write_results_page(name, template):
    with open("html/results/{0}.html".format(name), 'w') as outfile:
        outfile.write(template.render(league_name=name))


config = {
  'user': 'root',
  'passwd': '',
  'host': 'localhost',
  'db': 'auction',
  'charset': 'utf8'
}

db = MySQLdb.connect(**config)

cursor = db.cursor()

cursor.execute("SELECT name, sport FROM leagues")

leagues = {'baseball': [], 'football': []}

for row in cursor.fetchall():
    leagues[row[1]].append(row[0])

env = Environment(loader=FileSystemLoader('templates'))
results_template = env.get_template('results.html')

for league in leagues['baseball']:
    write_league_file(league, cursor)
    write_results_page(league, results_template)


for league in leagues['football']:
    write_league_file(league, cursor)
    write_results_page(league, results_template)

db.close()


index_template = env.get_template('index.html')

with open('html/index.html', 'w') as outfile:
    outfile.write(index_template.render(leagues=leagues))
