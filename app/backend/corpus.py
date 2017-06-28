import datetime
import sqlite3
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string
import operator
import math
import time

from numpy import cumprod, linspace, random

#from bokeh.plotting import figure, show, output_file
#from bokeh.models import DatetimeTickFormatter
#from bokeh.palettes import *
from math import pi
from datetime import datetime as dt


import numpy as np

testData = { "corpus1": {"start": "1794-6-13" , "end": "1794-12-25"}
			, "2" : {"start": "1796-6-10" , "end": "1797-2-28"}
			, "3" : {"start": "1796-6-10" , "end": "1798-5-25"}
		}

def getStatsCorpus(ids=[]):
	conn = sqlite3.connect("lingstats.db")
	c =  conn.cursor()

	sqlTermFreq = "select word, total(freq) from termfreq where docID>=%i and docID <=%i and pos_tag='n' group by word " % (ids[0], ids[-1])
	c.execute(sqlTermFreq)
	termfreq = {w: f for (w, f) in c}


	sqlDocInSplit = "select word, COUNT(word) from termfreq where docID>=%i and docID<=%i and pos_tag='n' group by word " % (ids[0], ids[-1])
	c.execute(sqlDocInSplit)
	docFreqSplit = {w: d for (w, d) in c}

	sqlDocOutSplit = "SELECT word, COUNT(word) FROM termfreq WHERE (docID<%i or docID>%i) and pos_tag='n' and " \
					 "word in (SELECT DISTINCT word from termfreq where docID>=%i and docID<=%i and pos_tag='n')  " \
					 "GROUP BY word " % (ids[0], ids[-1], ids[0], ids[-1])
	c.execute(sqlDocOutSplit)
	for (w, d) in c:
		docFreqSplit[w] /= d

		return termfreq, docFreqSplit


def tokenizeCorpus(corpus=[]):
	translate_table = dict((ord(char), None) for char in string.punctuation)
	stop = set(stopwords.words('german'))
	t = []
	for l in corpus:
		t += [i.lower() for i in word_tokenize(l.translate(translate_table)) if i.lower() not in stop and i.isalpha()]

	return t



class Corpus:
	id = []
	name = ""
	dates = {}
	content = []
	contentBag = []
	tf = {}
	idf = {}

	def __init__(self, cstart="", cend="", cname=""):
		self.getCorpus(cstart, cend)
		self.dates = {}
		self.dates["start"] = cstart
		self.dates["end"] = cend
		self.name = cname

	def getCorpus(self, start="", end=""):
		startDate = datetime.date(int(start.split('-')[0]),
								  int(start.split('-')[1]),
								  int(start.split('-')[2]))
		endDate = datetime.date(int(end.split('-')[0]),
								int(end.split('-')[1]),
								int(end.split('-')[2]))

		db = "example.db"
		conn = sqlite3.connect(db)
		c = conn.cursor()

		c.execute("select id, date from letters where year>=%s and month>=%s and day>=%s LIMIT 1;" % (
		startDate.year, startDate.month, startDate.day))
		startID = c.fetchall()[0][0]
		c.execute(
			"select id, date from letters where year<=%s and month<=%s and day<=%s and year !=0 ORDER BY id DESC LIMIT 1;" % (
			endDate.year, endDate.month, endDate.day))
		endID = c.fetchall()[0][0]

		sql = "SELECT id,content FROM letters where id>=%s and id <= %s ORDER BY id ASC;" % (startID, endID)
		c.execute(sql)
		self.id = [x for x in range(startID, endID+1)]
		self.content =[[row[1]] for row in c ]
		self.contentBag = [w for body in self.content for w in tokenizeCorpus(body)]
		self.tf, self.idf = getStatsCorpus(ids=self.id)


	def getInfo(self):
		print("Information Corpus %s:" % self.name)
		print("Starts at = ", self.dates["start"], " (id: ", self.id[0],")")
		print("Ends at = ", self.dates["end"], " (id: ", self.id[-1],")")
		print("Size: ", len(self.content))
		#print(self.tf)

	def getTfIDf(self, word=""):
		return self.tf.get(word, 0) * self.idf.get(word, 1)

	def getG2(self, word="", b = 0., d = 0.):
		a = self.tf.get(word,0.0001)
		c = sum(list(self.tf.values()))
		e1 = c * (a + b) / (c + d)
		e2 = d * (a + b) / (c + d)

		# print("a: ", a)
		# print("b: ", b)
		# print("c: ", c)
		# print("d: ", d)
		# print("e1: ", e1)
		# print("e2: ", e2)

		if a != 0 and b !=0:
			return 2 * (a * math.log(a/e1 , math.e) + b * math.log(b/e2,math.e ))
		else:
			return 0


	def getHighestRanked(self, n=10):
		tfidf = [(word, self.getTfIDf(word)) for word in self.tf.keys()]
		return sorted(tfidf, key=operator.itemgetter(1),reverse=True)[:n]


	def getWordCloudJS(self, n=20):
		return [{"word": w, "freq": f } for (w, f) in self.getHighestRanked(n)]

	def getPWordCloudJS(self, n=20):
		highest = self.getHighestRanked(n)
		print("highest", highest)
		max = highest[0][1]
		print("Maximum", max)
		return {w: float(f)/float(max) for (w, f) in highest}


class CorpusSplits:
	dates = {}
	corpusList = []
	tf = {}
	dateMap = {}

	def __init__(self):
		conn = sqlite3.connect("lingstats.db")
		c = conn.cursor()

		sqlTermFreq = "select docID, word, freq from termfreq WHERE pos_tag='n'"
		c.execute(sqlTermFreq)
		for (id, word, freq) in c:
			#print(id)
			if id not in self.tf.keys():
				self.tf[id] = {}
			self.tf[id][word] = freq
		conn.close()

		conn = sqlite3.connect("example.db")
		c = conn.cursor()
		sqlTermFreq = "select id, year, month, day from letters"
		c.execute(sqlTermFreq)
		self.dateMap = { id :{ "year": year, "month":month, "day":day } for (id, year, month, day) in c }

	def getIDsByName(self, word="", name=""):
		for c in self.corpusList:
			if c.name == name:
				return [ i  for i in c.id if self.tf.get(i, {}).get(word,0) != 0 ]
		return []

	def initByDate(self, datejs = {}):
		self.clear()
		for c in datejs.keys():
			tmp = Corpus(cstart=datejs[c]["start"], cend=datejs[c]["end"], cname=c)
			tmp.getInfo()
			self.corpusList.append(tmp)

	def getInfo(self):
			print("This Split contains ",len(self.corpusList), "corpus")
			for c in self.corpusList:
				c.getInfo()
				print("")

	def getG2(self, word = ""):
		g2list = []
		for i in range(0,len(self.corpusList)):
			#print("Corpus %i" % i)
			remainder = [elt for num, elt in enumerate(self.corpusList) if not num == i]
			b = sum([c.tf.get(word, 0) for c in remainder])
			d = sum([sum(c.tf.values()) for c in remainder])
			g2list.append(self.corpusList[i].getG2(word, b=b, d=d))

		return g2list

	def getG2_single(self, i, word = ""):
		remainder = [elt for num, elt in enumerate(self.corpusList) if not num == i]
		b = sum([c.tf.get(word, 0) for c in remainder])
		d = sum([sum(c.tf.values()) for c in remainder])
		a = self.corpusList[i].tf.get(word, 0.0001)
		c = sum(list(self.corpusList[i].tf.values()))
		e1 = c * (a + b) / (c + d)
		e2 = d * (a + b) / (c + d)
		if a != 0 and b !=0:
			return 2 * (a * math.log(a/e1 , math.e) + b * math.log(b/e2,math.e ))
		else:
			return 0


	def gettfidf(self, word=""):
		return [c.getTfIDf(word) for c in self.corpusList]

	def getWordCloudJS(self, n=20):
		return {c.name: c.getWordCloudJS(n) for c in self.corpusList}

	def getPWordCloudJS(self, n=20):
		return {c.name: c.getPWordCloudJS(n) for c in self.corpusList}

	def getPWordCloudJSG2(self, n=20):
		return {self.corpusList[c].name: self.getPWordCloudG2_single(c,n) for c in range(0,len(self.corpusList))}


	def getPWordCloudG2_single(self, corpus = None,n=10):
		highest = self.getHighestRankedG2(corpus,n)
		max = highest[0][1]
		#print("highest", highest)
		return {w: float(f) / float(max) for (w, f) in highest}

	def getHighestRankedG2(self, corpus = 0 , n=10):
		g2 = [(word, self.getG2_single( corpus, word)) for word in self.corpusList[corpus].tf.keys()]
		return sorted(g2, key=operator.itemgetter(1),reverse=True)[:n]

	def clear(self):
		self.dates = {}
		self.corpusList = []

	def getWordLine(self, word ="", step=5, ):

		plotDataDates = []
		plotDataIDs = []
		plotDataMeasure =[]

		for batchStart in list(self.dateMap.keys())[::step]:
			if batchStart+step > list(self.dateMap.keys())[-1]:
				break
			else:

				batch = range(batchStart, batchStart+step)

				#remainder = [elt for num, elt in enumerate(self.corpusList) if not num in batch]


				a = sum( [ self.tf.get(i,{}).get(word,0) for i in batch ] ) + 0.0001
				b = sum( [ self.tf.get(i,{}).get(word,0) for i in list(self.dateMap.keys()) if i not in batch ] ) + 0.0001

				c = sum( [ sum(self.tf.get(i,{}).values()) for i in batch])
				d = sum( [ sum(self.tf.get(i,{}).values()) for i in list(self.dateMap.keys()) if i not in batch ])

				e1 = c * (a + b) / (c + d)
				e2 = d * (a + b) / (c + d)
				g2 = 2 * (a * math.log(a / e1, math.e) + b * math.log(b / e2, math.e))

				try:

					years =  [ self.dateMap.get(i,{}).get("year",0) for i in batch if self.dateMap.get(i,{}).get("year",0) ]
					months = [ self.dateMap.get(i,{}).get("month",0) for i in batch if self.dateMap.get(i,{}).get("month",0)]
					days   = [ self.dateMap.get(i,{}).get("day",0) for i in batch if self.dateMap.get(i,{}).get("day",0) ]

					if len(years) == 0 or len ( months) == 0 or len(days) == 0:
						pass
					else:
						plotDataDates.append(dt(day=days[0], year=years[0], month=months[0]))
						plotDataIDs.append(batchStart)
						plotDataMeasure.append(g2)

				except (ValueError, ):
					pass



		return plotDataDates, plotDataIDs, plotDataMeasure


	# def plot(self,word = [], step = 100):
	# 	output_file("correlation.html", title="correlation.py example")
	# 	TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
	# 	plot = figure(x_axis_type="datetime", tools=TOOLS)
	# 
	# 	for (w,c) in zip(word, Category20[20]):
	# 		date, id, y = self.getWordLine(w, step = step)
	# 		plot.line(date, y, color=c, legend=w)
	# 
	# 
	# 
	# 
	# 
	# 	plot.xaxis.formatter = DatetimeTickFormatter(
	# 		hours=["%d %B %Y"],
	# 		days=["%d %B %Y"],
	# 		months=["%d %B %Y"],
	# 		years=["%d %B %Y"],
	# 	)
	# 	plot.xaxis.major_label_orientation = pi / 4
	# 	show(plot)


def main():

	c = CorpusSplits()
	#c.initByDate(testData)

	#c.getInfo()
	word="Faust"
	#print(word, c.gettfidf(word))
	#print(c.getPWordCloudJS(20))
	#print(word, c.getG2(word))

	#print(c.getPWordCloudJSG2(10))
	#print(c.getPWordCloudJS(10))


	#print(c.getWordLine(word=word, step=4))


if __name__ == "__main__":
	main()