#!/usr/bin/python

import MySQLdb
import json
import os
import boto3
from jinja2 import Environment, FileSystemLoader
import ConfigParser


def write_results_file(league, cursor):
    cursor.execute("""
        SELECT p.name, t.name, p.position, pw.price, pw.time
        FROM players_won pw
        JOIN players p
          ON p.playerid=pw.playerid
        JOIN teams t
          ON pw.teamid=t.id 
        WHERE pw.leagueid = '{0}'
    """.format(league['id']))

    players = cursor.fetchall()

    data = {'data': players}

    data_dir = "data/results"
    data_file = os.path.join(data_dir, "{0}.json".format(league['name']))

    with open(data_file, 'w') as outfile:
        json.dump(data, outfile)


def write_results_page(name, template):
    with open("html/results/{0}.html".format(name), 'w') as outfile:
        outfile.write(template.render(league_name=name))


def write_contracts_file(name, cursor):
    cursor.execute("""
        SELECT c.team, p.name, c.current_cost, c.years_left, c.broken
        FROM contracts c
        JOIN players p
          ON p.playerid=c.player
        WHERE league = '{0}'
    """.format(name))

    players = cursor.fetchall()

    data = {'data': players}

    data_dir = "data/contracts"
    data_file = os.path.join(data_dir, "{0}.json".format(name))

    with open(data_file, 'w') as outfile:
        json.dump(data, outfile)


def write_contracts_page(name, template):
    with open("html/contracts/{0}.html".format(name), 'w') as outfile:
        outfile.write(template.render(league_name=name))


# Write a file to S3
def write_file(bucket, local_path, remote_path=''):

    if not remote_path:
        remote_path = local_path

    with open(local_path, 'r') as data:
        bucket.put_object(Key=remote_path, Body=data, ContentType='text/html')


config = ConfigParser.ConfigParser()
config.read('db.ini')

section = 'prod'

dbconfig = {
  'user': config.get(section, 'user'),
  'passwd': config.get(section, 'password'),
  'host': config.get(section, 'hostname'),
  'port': config.getint(section, 'port'),
  'db': config.get(section, 'schema'),
  'charset': config.get(section, 'charset')
}

db = MySQLdb.connect(**dbconfig)

cursor = db.cursor()

cursor.execute("SELECT id, name, sport FROM leagues")

leagues = {'baseball': [], 'football': []}

for row in cursor.fetchall():
    leagues[row[2]].append({'id': row[0], 'name': row[1]})

env = Environment(loader=FileSystemLoader('templates'))
results_template = env.get_template('results.html')
contracts_template = env.get_template('contracts.html')

for league in leagues['baseball']:
    write_results_file(league, cursor)
    write_results_page(league['name'], results_template)
    write_contracts_file(league['name'], cursor)
    write_contracts_page(league['name'], contracts_template)


for league in leagues['football']:
    write_results_file(league, cursor)
    write_results_page(league['name'], results_template)
    write_contracts_file(league['name'], cursor)
    write_contracts_page(league['name'], contracts_template)

db.close()


index_template = env.get_template('index.html')

with open('html/index.html', 'w') as outfile:
    outfile.write(index_template.render(leagues=leagues))

s3 = boto3.resource('s3')
bucket = s3.Bucket('twoguysandadream.com')

write_file(bucket, os.path.join('html', 'index.html'), 'index.html')

for directory in ['data/results', 'html/results', 'data/contracts', 'html/contracts']:
    for file in os.listdir(directory):
        write_file(bucket, os.path.join(directory, file))
