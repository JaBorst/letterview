import sqlite3
import datetime
import re
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string

testData = { "1": {"start": "1794-6-13" , "end": "1794-12-25"}
			, "2" : {"start": "1796-6-10" , "end": "1797-2-28"}
			, "3" : {"start": "1796-6-10" , "end": "1798-5-25"}
		}




def getCorpus(start="",end=""):
	
	startDate = datetime.date(int(start.split('-')[0]),
							  int(start.split('-')[1]),
							  int(start.split('-')[2]))
	endDate = datetime.date(int(end.split('-')[0]),
							  int(end.split('-')[1]),
							  int(end.split('-')[2]))
	
	db = "/home/jb/git/LettersView/src/src/example.db"
	conn = sqlite3.connect(db)
	c = conn.cursor()
	
	c.execute("select date,id from letters;")
	
	dateIndexDict = {}
	
	for letter in c:
		r1 = re.compile('^[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}$')
		r2 = re.compile('^[0-9]{1,2}\.[0-9]{4}$')
		r3 = re.compile('^[0-9]{4}$')
		if r1.match(letter[0]):
			d = datetime.date(int(letter[0].split('.')[2]),
							  int(letter[0].split('.')[1]),
							  int(letter[0].split('.')[0]))
			
			dateIndexDict[d] = letter[1]
			
		elif r2.match(letter[0]):
			pass # maybe later implement			
		elif r3.match(letter[0]):
			pass
		else:
			#print(letter)
			pass
	

	startID = 0
	for d in dateIndexDict.keys():
		if d >= startDate:
			print ("StartDate found" , d, " for ", start)
			startID = dateIndexDict[d]
			break

	endID = 0
	for d in dateIndexDict.keys():
		if d > endDate:
			print ("EndDate found" , lastDate, " for ", end)
			endID = dateIndexDict[lastDate]
			break
		lastDate = d
		
	idList = [str(x) for x in range(startID, endID)]
	sql="SELECT CONTENT FROM letters where id in (" + ','.join(idList) + ")"
	#print(sql)
	c.execute(sql)
	corpus = []
	for row in c:
		corpus.append(row[0])
		
	return corpus
		



def getCorpus2(start="", end=""):
	
	startDate = datetime.date(int(start.split('-')[0]),
							  int(start.split('-')[1]),
							  int(start.split('-')[2]))
	endDate = datetime.date(int(end.split('-')[0]),
							  int(end.split('-')[1]),
							  int(end.split('-')[2]))
	
	db = "/home/jb/git/LettersView/src/src/example.db"
	conn = sqlite3.connect(db)
	c = conn.cursor()
	
	c.execute("select id, date from letters where year>=%s and month>=%s and day>=%s LIMIT 1;" % (startDate.year, startDate.month, startDate.day))
	startID = c.fetchall()[0][0]
	c.execute("select id, date from letters where year<=%s and month<=%s and day<=%s and year !=0 ORDER BY id DESC LIMIT 1;"% (endDate.year, endDate.month, endDate.day))
	endID = c.fetchall()[0][0]
	
	sql="SELECT CONTENT FROM letters where id>=%s and id <= %s;" % (startID, endID)
	#print(sql)
	c.execute(sql)
	corpus = []
	for row in c:
		corpus.append(row[0])
		
	return corpus
	
	
def tokenizeCorpus(corpus=[]):
	translate_table = dict((ord(char), None) for char in string.punctuation)
	stop = set(stopwords.words('german'))
	t = []
	for l in corpus:
		t+=[i.lower() for i in word_tokenize(l.translate(translate_table)) if i.lower() not in stop and i.isalpha()]
		
	
	return t

def getCorpusJSON(data):
	js = {}
	for l in data.keys():
		#print(data[l]['start'])
		#print(data[l]['end'])
		letters = tokenizeCorpus(getCorpus2(data[l]["start"],data[l]["end"]))
		js[l] = letters
		#print(letters)
	return js



def getWordCloudWords(corpora):
		
	freq = {}
	for c in corpora.keys():
		corpus = corpora[c]
		f = FreqDist(corpus)
		for w,count in f.most_common(10):
			if c not in freq.keys():
				freq[c] = {}	
			freq[str(c)][w] = count
		
	return freq
		



def main():
	print(2)
	fd = getWordCloudWords(getCorpusJSON(testData))
	print (fd)
	
if __name__ == '__main__':
	main()