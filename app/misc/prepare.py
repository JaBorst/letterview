#!/bin/python

import re
from urllib.request import urlretrieve

import requests
import sqlite3
import time
from random import randint,random


url='http://www.wissen-im-netz.info/literatur/goethe/briefe/schiller/'
hundreds = [1, 100, 200, 300 ,400 ,500, 600, 700, 800, 900]
num = [x for x in range(99)]
split1='<td width="80%" valign="top">'
split2 ='<font face="Symbol">'

dateDirectionTable = {}



def get_directional_table():
	tablesURL= 'http://www.wissen-im-netz.info/literatur/goethe/briefe/schiller/'
	years = [ x for x in range(1794, 1806) ]
	pattern = re.compile("^[0-9]+\.$")

	dateDirectionTable[0]=["18.10.1829",'K',(1892,10,18)]

	for year in years:
		tURL = tablesURL + "/" + str(year) + ".htm"
		dl = requests.get(tURL)
		if dl.status_code != 200:
			print("Error: "+tURL +" gave an "+str(dl.status_code))
		print(tURL)
		arr = dl.text.split("<table")[2].split("</table>")[0].split("<tr>")

		cleanArr = []
		for row in arr:
			rowArr = re.split(" +",re.sub("\s+?"," ",re.sub("<.*?>", " ", row)))
			#print(len(rowArr))

			if "border" not in rowArr[1] and "Datum" not in rowArr[1]:
				#print(rowArr)
				date = rowArr[1]
				dateList = [0,0,0] #default
				direction = ""
				num = 0
				
				#print(date)
				r1 = re.compile('^[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}$')
				r2 = re.compile('^[0-9]{1,2}\.[0-9]{4}$')
				r3 = re.compile('^[0-9]{4}$')
				
				if r1.match(date):
					dateList[0] = date.split('.')[2]
					dateList[1] = date.split('.')[1]
					dateList[2] = date.split('.')[0]
				elif r2.match(date):
					dateList[0] = date.split('.')[1]
					dateList[1] = date.split('.')[0]
				elif r3.match(date):
					dateList[0] = date.split('.')[0]

				#print (dateList)
				
				
				

				if pattern.match(rowArr[3]):
					num = int(rowArr[3].replace(".","").strip())
					direction = 'S'
					dateDirectionTable[num] = [date, direction, dateList]
					#print(str(num) + " an schiller")

				if pattern.match(rowArr[4]):
					num = int(rowArr[4].replace(".","").strip())
					direction = 'G'
					dateDirectionTable[num] = [date, direction, dateList]
					#print(str(num) + " an Goethe")
		#break
			#time.sleep(randint(2,5))				
	return dateDirectionTable


def main():
	
	infotable = get_directional_table()
	#print(infotable)


	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	c.execute('''PRAGMA encoding="UTF-8";''')
	c.execute('''CREATE TABLE IF NOT EXISTS letters
             (id INT, date TEXT,  year INT, month INT, day INT, content TEXT, url TEXT, for TEXT)''')



	for h in hundreds:
		for n in num:
			if h == 1:
				letterURL = url + str(h) + "/" + str(n).zfill(3) + ".htm"
				letterNum = n
			else:
				letterURL = url + str(h) + "/" + str(h+n).zfill(3) + ".htm"
				letternum = h+n

			dl = requests.get(letterURL)
			if dl.status_code != 200:
				print("Error: "+ letterURL +" gave an "+str(dl.status_code))

			print(letterURL)
			#print(dl.text.encode("utf8"))

			#filename = "letters/" + str(h) + "/" + str(n).zfill(3) + ".html"
			html = re.sub("<.*?>", " ", dl.text.split(split1)[1].split(split2)[0].replace('</font>','')).replace('&nbsp;',' ').replace('"','""').strip()
			c.execute('insert INTO letters VALUES( ? , ? , ? , ? , ? , ? , ? , ? )', (h+n, infotable[h+n][0], infotable[h+n][2][0], infotable[h+n][2][1], infotable[h+n][2][2], html, letterURL, infotable[h+n][1]))
			conn.commit()
			#print(html)

			time.sleep(random())
		time.sleep(randint(2,5))




if __name__ == "__main__":
	#get_directional_table()
	main()
