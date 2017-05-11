from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords

from collections import Counter

import string
import sqlite3


def tokenizeCorpus(corpus=[]):
	translate_table = dict((ord(char), None) for char in string.punctuation)
	stop = set(stopwords.words('german'))
	t = []
	for l in corpus:
		t += [i.lower() for i in word_tokenize(l.translate(translate_table)) if i.lower() not in stop and i.isalpha()]

	return t


def main():
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	c.execute("SELECT content from letters;")

	termfreq = []
	dokfreq = Counter()
	for letter in c:
		tok = tokenizeCorpus(letter)
		termfreq+=tok

		dokfreq += Counter(list(set(tok)))

	c.execute("CREATE TABLE IF NOT EXISTS termfreq ( word TEXT, freq INT)")
	c.execute("CREATE TABLE IF NOT EXISTS dokfreq ( word TEXT, freq INT)")

	print(Counter(termfreq).most_common(20))
	print(Counter(dokfreq.most_common(20)))

	termfreqCounter = Counter(termfreq)
	dokfreqCounter = dokfreq

	for w in termfreqCounter:
		c.execute("INSERT INTO termfreq VALUES ( ? , ? )", (w, str(termfreqCounter[w])))

	conn.commit()
	for w in dokfreqCounter:
		c.execute("INSERT INTO dokfreq VALUES ( ? , ? )", (w, str(dokfreqCounter[w])))
	conn.commit()


if __name__ == "__main__":
	main()