from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords

from collections import Counter

import string
import sqlite3
import treetaggerwrapper
tagger = treetaggerwrapper.TreeTagger(TAGLANG='de')

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
	c.execute("SELECT id, content from letters;")

	termfreq = []
	dokfreq = Counter()
	for (id, letter) in c:
		tok = tokenizeCorpus(letter)
		termfreq+=tok

		dokfreq += Counter(list(set(tok)))

	c.execute("CREATE TABLE IF NOT EXISTS termfreq (docID INT, word TEXT, freq INT, pos_tag TEXT)")
	c.execute("CREATE TABLE IF NOT EXISTS dokfreq ( word TEXT, freq INT)")

	print(Counter(termfreq).most_common(20))
	print(Counter(dokfreq.most_common(20)))

	termfreqCounter = Counter(termfreq)
	dokfreqCounter = dokfreq

	for w in termfreqCounter:
		c.execute("INSERT INTO termfreq VALUES ( ? , ? , ? , ? )", (id, w, str(termfreqCounter[w], tag)))

	conn.commit()
	for w in dokfreqCounter:
		c.execute("INSERT INTO dokfreq VALUES ( ? , ? )", (w, str(dokfreqCounter[w])))
	conn.commit()


if __name__ == "__main__":
	main()