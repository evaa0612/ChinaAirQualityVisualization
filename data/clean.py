# this python code retrieves data from the database and format the data into something that is visualizable
import sqlite3
import json
from datetime import datetime

# define a function to convert timestamp
def convert_time(timestamp):
    return str(datetime.fromtimestamp(timestamp))[:10]

# connect to database
year = str(input()) # enter which year's data you want to retrieve
conn = sqlite3.connect('aqi.sqlite')
cur = conn.cursor()

# select all the cities
cur.execute("SELECT division, pinyinName from areas WHERE bottom = 'FALSE'")
city_list = cur.fetchall()

# select all the aqi from all cities
all_city_aqi = {} # a dict that stores all the aqi data for every city
all_city_encoding = {}
all_city_province = {}
month_list = [year+'-01',year+'-02',year+'-03',year+'-04',year+'-05',year+'-06',year+'-07',year+'-08',year+'-09',year+'-10',year+'-11',year+'-12']
for pair in city_list:
    # find the division, pinyin of that city
    division = str(pair[0])
    all_city_province[division[:2]] = all_city_province.get(division[:2],[])
    all_city_province[division[:2]].append(division)
    pinyin = pair[1]
    if division[2:] == '0000': # divisin ending with '0000' is a province
        all_city_encoding[division] = pinyin
    cur.execute("SELECT recordDate, value from aqi WHERE division = (?) ORDER BY recordDate",(division,))
    data = cur.fetchall()
    data = [[convert_time(pair[0]),pair[1]] for pair in data]
    new_data = {}
    # create a dictionary to store the data retrived from the database
    for m in month_list:
        new_data[m] = [0, 0]
    for pair in data:
        if pair[0][:4] != year:
            continue # skip the data if it is not in the year specified
        temp_month = pair[0][:7]
        new_data[temp_month][0] += pair[1]
        new_data[temp_month][1] += 1
    parsed_data = []
    for i in new_data.keys():
        try:
            # calculate the mean aqi of a month so that it is more representable
            parsed_data.append([i, new_data[i][0]*1.0/new_data[i][1]])
        except:
            continue
    all_city_aqi[division] = parsed_data

# remove duplicated keys
for key in all_city_province.keys():
    if len(all_city_province[key]) != 1:
        all_city_province[key].remove(key+'0000')

cur.execute('SELECT division, pinyinName FROM areas WHERE bottom = "FALSE"')
area_encoding = cur.fetchall()
all_city_pinyin = {}
for pair in area_encoding:
    all_city_pinyin[pair[0]] = pair[1]
conn.close()

# write to json files that can be loaded to html and visualize
with open('all_city_aqi_'+year+'.json','w') as f:
    f.write(json.dumps(all_city_aqi))
with open('all_city_encoding.json','w') as f:
    f.write(json.dumps(all_city_encoding))
with open('all_city_province.json','w') as f:
    f.write(json.dumps(all_city_province))
with open('all_city_pinyin.json','w') as f:
    f.write(json.dumps(all_city_pinyin))
