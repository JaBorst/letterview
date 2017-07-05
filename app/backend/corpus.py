import datetime
import sqlite3
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string
import operator
import math
import time

from numpy import cumprod, linspace, random

from bokeh.plotting import figure, show, output_file,save
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import file_html,components

from bokeh.resources import CDN

from bokeh.palettes import *
from math import pi
from datetime import datetime as dt

termfreqtable = "termfreq"
lingstatDB = "lingstatsStem.db"
rel_pos_tag = 'n'
measurement = 'tfidf'
allowed_measurements = ["tfidf", "g2", "g2idf"]
g2scoringtag='global'


import numpy as np

testData = { "corpus1": {"start": "1794-6-13" , "end": "1794-12-25"}
			, "corpus2" : {"start": "1796-6-10" , "end": "1797-2-28"}
			#, "3" : {"start": "1796-6-10" , "end": "1798-5-25"}
		}

def getStatsCorpus(ids=[]):
	conn = sqlite3.connect(lingstatDB)
	c =  conn.cursor()

	sqlTermFreq = "select word, total(freq) from %s where docID>=%i and docID <=%i and pos_tag='%s' group by word " % (termfreqtable,ids[0], ids[-1],rel_pos_tag)
	c.execute(sqlTermFreq)
	termfreq = {w: f for (w, f) in c}


	sqlDocInSplit = "select word, COUNT(word) from %s where docID>=%i and docID<=%i and pos_tag='%s' group by word " % (termfreqtable, ids[0], ids[-1],rel_pos_tag)
	c.execute(sqlDocInSplit)
	docFreqSplit = {w: d for (w, d) in c}

	sqlDocOutSplit = "SELECT word, COUNT(word) FROM %s WHERE (docID<%i or docID>%i) and pos_tag='%s' and " \
					 "word in (SELECT DISTINCT word from %s where docID>=%i and docID<=%i and pos_tag='%s')  " \
					 "GROUP BY word " % (termfreqtable, ids[0], ids[-1],rel_pos_tag, termfreqtable, ids[0], ids[-1],rel_pos_tag)
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
		if cstart != "" and cend != "":
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

	def getCorpusId(self, ids=[]):
		self.id = ids
		self.id.sort()
		startID = self.id[0]
		endID = self.id[-1]
		db = "example.db"
		conn = sqlite3.connect(db)
		c = conn.cursor()
		sql = "SELECT id,content FROM letters where id>=%s and id <= %s ORDER BY id ASC;" % (startID, endID)
		c.execute(sql)
		self.content = [[row[1]] for row in c]
		self.contentBag = [w for body in self.content for w in tokenizeCorpus(body)]
		self.tf, self.idf = getStatsCorpus(ids=self.id)

	def getInfo(self):
		print("Information Corpus %s:" % self.name)
		#print("Starts at = ", self.dates["start"], " (id: ", self.id[0],")")
		#print("Ends at = ", self.dates["end"], " (id: ", self.id[-1],")")
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
	df = {}

	def __init__(self):
		conn = sqlite3.connect(lingstatDB)
		c = conn.cursor()

		sqlTermFreq = "select docID, word, freq from %s WHERE pos_tag='%s'" % (termfreqtable,rel_pos_tag)
		c.execute(sqlTermFreq)
		for (id, word, freq) in c:
			#print(id)
			if id not in self.tf.keys():
				self.tf[id] = {}
			self.tf[id][word] = freq
			self.df[word] = self.df.get(word,0) +1
			
		conn.close()

		conn = sqlite3.connect("example.db")
		c = conn.cursor()
		sqlTermFreq = "select id, year, month, day from letters"
		c.execute(sqlTermFreq)
		self.dateMap = { id :{ "year": year, "month":month, "day":day } for (id, year, month, day) in c }
		print("Initialized")


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

	def initByID(self, idListOfList=[]):
		self.clear()
		for id in idListOfList:
			tmp = Corpus(cname="Brief" + str(id))
			tmp.getCorpusId(id)
			#tmp.getInfo()
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
		
	def getG2_single_global(self, i, word = ""):
		remainderIds = set(self.tf.keys()) - set(self.corpusList[i].id)
		focussedIds = self.corpusList[i].id
		a = sum([self.tf.get(id,{}).get(word, 0.0001) for id in focussedIds])
		b = sum([self.tf.get(id,{}).get(word, 0) for id in remainderIds])
		c = sum([sum(list(self.tf.get(id,{}).values())) for id in focussedIds])
		#print(self.tf.get(id,{}).values())
		d = sum([sum(list(self.tf.get(id,{}).values())) for id in remainderIds])
		
		#print(a,b,c,d)
		
		e1 = c * (a + b) / (c + d)
		e2 = d * (a + b) / (c + d)
		if a != 0 and b !=0:
			return 2 * (a * math.log(a/e1 , math.e) + b * math.log(b/e2,math.e ))
		else:
			return 0
		
	# def getG2_single_global(self, letterId, word = ""):
	# 	a = self.tf.get(letterId,{}).get(word, 0.0001)
	# 	b = sum([self.tf.get(id,{}).get(word, 0) for id in self.tf.keys() if id != letterId])
	# 	c = sum(list(self.tf.get(letterId,{}).values()))
	# 	print(self.tf.get(letterId,{}).values())
	# 	d = sum([sum(self.tf.get(id,{}).values()) for id in self.tf.keys() if id != letterId])
	# 	
	# 	print(a,b,c,d)
	# 	
	# 	e1 = c * (a + b) / (c + d)
	# 	e2 = d * (a + b) / (c + d)
	# 	if a != 0 and b !=0:
	# 		return 2 * (a * math.log(a/e1 , math.e) + b * math.log(b/e2,math.e ))
	# 	else:
	# 		return 0


	def gettfidf(self, word=""):
		return [c.getTfIDf(word) for c in self.corpusList]

	def getWordCloudJS(self, n=20):
		return {c.name: c.getWordCloudJS(n) for c in self.corpusList}

	def getPWordCloudJS(self, n=20):
		return {c.name: c.getPWordCloudJS(n) for c in self.corpusList}

	def getPWordCloudJSG2(self, n=20):
		return {self.corpusList[c].name: self.getPWordCloudG2_single(c,n) for c in range(0,len(self.corpusList))}

	def getPWordCloudJSG2IDF(self, n=20):
		return {self.corpusList[c].name: self.getPWordCloudG2IDF_single(c,n) for c in range(0,len(self.corpusList))}


	def getPWordCloudG2_single(self, corpus = None,n=10):
		global g2scoringtag
		if g2scoringtag == 'global':
			highest = self.getHighestRankedG2_global(corpus,n)
		elif g2scoringtag == 'local':
			highest = self.getHighestRankedG2(corpus,n)
					
		max = highest[0][1] if highest[0][1] !=0 else 1
		
		#print("highest", highest)
		return {w: float(f) / float(max) for (w, f) in highest}
	
	def getPWordCloudG2IDF_single(self, corpus = None,n=10):
		global g2scoringtag
		if g2scoringtag == 'global':
			highest = self.getHighestRankedG2IDF_global(corpus,n)
		elif g2scoringtag == 'local':
			highest = self.getHighestRankedG2IDF(corpus,n)
		max = highest[0][1] if highest[0][1] !=0 else 1
		#print("highest", highest)
		return {w: float(f) / float(max) for (w, f) in highest}

	def getHighestRankedG2_global(self, corpus = 0 , n=10):
		g2 = [(word, self.getG2_single_global( corpus, word)) for word in self.corpusList[corpus].tf.keys()]
		return sorted(g2, key=operator.itemgetter(1),reverse=True)[:n]
	
	def getHighestRankedG2IDF_global(self, corpus = 0 , n=10):
		g2 = [(word, self.getG2_single_global( corpus, word)/self.df.get(word, 1)) for word in self.corpusList[corpus].tf.keys()]
		return sorted(g2, key=operator.itemgetter(1),reverse=True)[:n]
	
	def getHighestRankedG2(self, corpus = 0 , n=10):
		g2 = [(word, self.getG2_single( corpus, word)) for word in self.corpusList[corpus].tf.keys()]
		return sorted(g2, key=operator.itemgetter(1),reverse=True)[:n]
	
	def getHighestRankedG2IDF(self, corpus = 0 , n=10):
		g2 = [(word, self.getG2_single( corpus, word)/self.df.get(word, 1)) for word in self.corpusList[corpus].tf.keys()]
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

	def getWordLineG2IDF(self, word ="", step=5, ):

	
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
				
				g2idf = g2 / self.df.get(word,1)
				
				try:
	
					years =  [ self.dateMap.get(i,{}).get("year",0) for i in batch if self.dateMap.get(i,{}).get("year",0) ]
					months = [ self.dateMap.get(i,{}).get("month",0) for i in batch if self.dateMap.get(i,{}).get("month",0)]
					days   = [ self.dateMap.get(i,{}).get("day",0) for i in batch if self.dateMap.get(i,{}).get("day",0) ]
	
					if len(years) == 0 or len ( months) == 0 or len(days) == 0:
						pass
					else:
						plotDataDates.append(dt(day=days[0], year=years[0], month=months[0]))
						plotDataIDs.append(batchStart)
						plotDataMeasure.append(g2idf)
	
				except (ValueError, ):
					pass
	
	
	
		return plotDataDates, plotDataIDs, plotDataMeasure


	def plot(self, filename="wordline.html" , word = [], step = 100):
		output_file("../frontend/"+filename, title="correlation.py example")
		TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
		plot = figure(x_axis_type="datetime", tools=TOOLS)

		for (w,c) in zip(word, Category20[20]):
			date, id, y = self.getWordLineG2IDF(w, step = step)
			plot.line(date, y, color=c, legend=w, muted_color=c, muted_alpha=0.01,)





		plot.xaxis.formatter = DatetimeTickFormatter(
			hours=["%d %B %Y"],
			days=["%d %B %Y"],
			months=["%d %B %Y"],
			years=["%d %B %Y"],
		)
		plot.xaxis.major_label_orientation = pi / 4
		plot.legend.click_policy = "mute"

		save(plot)
		return filename


	def set_pos_tag(self, pt = 'n'):
		global rel_pos_tag
		rel_pos_tag = pt
		self.__init__()
		
	def set_measure(self, measure = 'tfidf'):
		global measurement
		if measure in allowed_measurements:
			measurement = measure
			print("Measurement changed to: ", measurement)
			
	def g2scoringTag(self, tag = "global"):
		global g2scoringtag
		g2scoringtag=tag
		print("Scoring G2 now ",g2scoringtag)
		
	def getPWordCloud(self, num=20, method=""):
		useMethod = ""
		if method != "":
			useMethod = method
		else:
			global measurement
			useMethod = measurement
			
		if measurement == "tfidf":
			return self.getPWordCloudJS(n=num)
		elif measurement == 'g2':
			return self.getPWordCloudJSG2(n=num)
		elif measurement == 'g2idf':
			return self.getPWordCloudJSG2IDF(n=num)

def main():

	#c = CorpusSplits()
	#c.initByDate(testData)


	c = CorpusSplits()

	idjs = {"corpus1": {"idList" : [1]},
			"corpus2": {"idList" : [2]},
			"corpus3": {"idList" : [3]} }

	c.initByDate(testData)

	#c.getInfo()
	#word="Faust"
	#print(word, c.gettfidf(word))
	#print(c.getPWordCloudJS(20))
	#print(word, c.getG2(word))

	print(c.getPWordCloudJSG2(10))
	c.set_pos_tag('v')
	c.initByDate(testData)
	print(c.getPWordCloudJSG2(10))
	#print(c.getPWordCloudJS(10))

	#print(c.getIDsByName(word="Horen", name="corpus1"))
	#print(c.getWordLine(word=word, step=4))

	#c.plot(filename="wordline.html", word=["Faust", "Horen", "Brief", "Briefen", "Briefe"], step=5)


if __name__ == "__main__":
	main()
