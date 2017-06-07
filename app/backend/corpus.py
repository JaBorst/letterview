import datetime
import sqlite3
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string
import operator

import numpy as np

testData = { "corpus1": {"start": "1794-6-13" , "end": "1794-12-25"}
			, "2" : {"start": "1796-6-10" , "end": "1797-2-28"}
			, "3" : {"start": "1796-6-10" , "end": "1798-5-25"}
		}

def getStatsCorpus(ids=[]):
	conn = sqlite3.connect("lingstats.db")
	c =  conn.cursor()

	sqlTermFreq = "select word, total(freq) from termfreq where docID>=%i and docID <=%i group by word " % (ids[0], ids[-1])
	c.execute(sqlTermFreq)
	termfreq = {w: f for (w, f) in c}


	sqlDocInSplit = "select word, COUNT(word) from termfreq where docID>=%i and docID<=%i group by word " % (ids[0], ids[-1])
	c.execute(sqlDocInSplit)
	docFreqSplit = {w: d for (w, d) in c}

	sqlDocOutSplit = "SELECT word, COUNT(word) FROM termfreq WHERE (docID<%i or docID>%i) and " \
					 "word in (SELECT DISTINCT word from termfreq where docID>=%i and docID<=%i)  " \
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

	def gettfidf(self, word=""):
		return [c.getTfIDf(word) for c in self.corpusList]

	def getWordCloudJS(self, n=20):
		return {c.name: c.getWordCloudJS(n) for c in self.corpusList}

	def getPWordCloudJS(self, n=20):
		return {c.name: c.getPWordCloudJS(n) for c in self.corpusList}

	def clear(self):
		self.dates = {}
		self.corpusList = []


def main():

	c = CorpusSplits()
	c.initByDate(testData)

	c.getInfo()
	word="zeitschrift"
	print(word, c.gettfidf(word))
	print(c.getPWordCloudJS(20))

if __name__ == "__main__":
	main()