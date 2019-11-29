import urllib.request, urllib.parse, urllib.error
import json
import ssl
import sqlite3
import xml.etree.ElementTree as ET

conn = sqlite3.connect('mpdatabase.sqlite')
cur = conn.cursor()


# Make some fresh tables using executescript()
cur.executescript('''

CREATE TABLE IF NOT EXISTS Gender (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    gender    TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Party (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    party   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Startyear (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    startyear   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Endyear (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    endyear   TEXT UNIQUE
);


CREATE TABLE IF NOT EXISTS MP (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT  UNIQUE,
    constituency TEXT  UNIQUE,
    twitter TEXT  UNIQUE,
    gender_id  INTEGER,
    party_id  INTEGER,
    startyear_id INTEGER,
    endyear_id INTEGER

);
''')


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#ExtractingNamesOfAllMembers
urlx = 'http://data.parliament.uk/membersdataplatform/services/mnis/members/query/House=Commons%7CMembership=all/'
xml = urllib.request.urlopen(urlx, context=ctx)
datax = xml.read()

root = ET.fromstring(datax)

serviceurl = 'http://lda.data.parliament.uk/members.json?'
#Get name and start/end dates for all those members of the house of commons only

countnotfound = 0

#member_start_end = {}
for member in root.findall('Member'):
    name = member.find('DisplayAs').text
    house = member.find('House').text
    if not house.startswith('Commons'):
        continue
    start = member.find('HouseStartDate').text
    start_year = start[0:4]
    ended = member.find('HouseEndDate').text
    end_year = ended[0:4]
    #member_start_end[name] = {'Start_Year': start_year, 'End_Year': end_year}
    #print(name, start_year, end_year)

#Then use name to find party credentials
    fullName = name
    if len(fullName) < 1: break

    parms = dict()
    parms['fullName'] = fullName
    url = serviceurl + urllib.parse.urlencode(parms)


    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()

    try:
        js = json.loads(data)
    except:
        js = None

    #print(js)


    if js['result']['totalResults'] == 0:
        #print('Total results', '0' , 'Please try again and ensure you spell the name correctly e.g. Greg Hands')
        print('Error, name not found. Attempting to find next member name in list.')
        countnotfound += 1
        continue


    name = js['result']['items'][0]['fullName']['_value']
    constituency = js['result']['items'][0]['constituency']['label']['_value']
    gender = js['result']['items'][0]['gender']['_value']
    party = js['result']['items'][0]['party']['_value']
    print('Name:', name)
    print('Constituency:', constituency)
    print('Gender:', gender)
    print('Party:', party)
    print('MP from:', start_year, 'to', end_year)

    try:
        twitter = js['result']['items'][0]['twitter']['_value']
        print('Twitter:', twitter)

    except:
        twitter = 0


    print('Successfully retrieved')
    #print('Successfully retrieved', len(data), 'characters')
    #print(json.dumps(js, indent=4))


    cur.execute('''INSERT OR IGNORE INTO Gender (gender)
        VALUES ( ? )''', ( gender, ) )
    cur.execute('SELECT id FROM Gender WHERE gender = ? ', (gender, ))
    gender_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Party (party)
        VALUES ( ? )''', ( party, ) )
    cur.execute('SELECT id FROM Party WHERE party = ? ', (party, ))
    party_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Startyear (startyear)
        VALUES ( ? )''', ( start_year, ) )
    cur.execute('SELECT id FROM Startyear WHERE startyear = ? ', (start_year, ))
    startyear_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Endyear (endyear)
        VALUES ( ? )''', ( end_year, ) )
    cur.execute('SELECT id FROM Endyear WHERE endyear = ? ', (end_year, ))
    endyear_id = cur.fetchone()[0]


    cur.execute('''INSERT OR REPLACE INTO MP
        (name, constituency, gender_id, party_id, startyear_id, endyear_id)
        VALUES ( ?, ?, ?, ?, ?, ?)''',
        ( name, constituency, gender_id, party_id, startyear_id, endyear_id) )

    conn.commit()

    if twitter is not 0:

        cur.execute('''INSERT OR REPLACE INTO MP
            (name, constituency, gender_id, party_id, startyear_id, endyear_id, twitter)
            VALUES ( ?, ?, ?, ?, ?, ?, ?)''',
            ( name, constituency, gender_id, party_id, startyear_id, endyear_id, twitter) )

        conn.commit()

    print('Database \'mpdatabase.sqlite\' successfully updated')
print('Database completed', 'Number of MPs not found:', countnotfound)
