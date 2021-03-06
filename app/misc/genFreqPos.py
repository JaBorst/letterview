from nltk import word_tokenize, FreqDist
import nltk
from nltk.corpus import stopwords
import re
pattern_noun = re.compile("^NN")
pattern_verb = re.compile("^VV")
pattern_adj = re.compile("^AD")

from nltk.stem import WordNetLemmatizer


from collections import Counter

import string
import sqlite3
import treetaggerwrapper
tagger = treetaggerwrapper.TreeTagger(TAGLANG='de')

wl = WordNetLemmatizer()

def tokenizeCorpusWeighted(corpus=""):
	global tagger
	translate_table = dict((ord(char), None) for char in string.punctuation)
	sentences = nltk.sent_tokenize(corpus)  # tokenize sentences

	words = []  # empty to array to hold all nouns
	weights = {}

	for sentence in sentences:
		for line in tagger.tag_text(sentence):
			#print(line)
			word = line.split("\t")[0]
			pos = line.split("\t")[1]
			#print(word, pos)
			if pattern_noun.match(pos):
				words.append(word)
				weights[word] = 'n'
			elif pattern_adj.match(pos):
				words.append(word)
				weights[word] = 'a'
			elif pattern_verb.match(pos):
				words.append(word)
				weights[word] = 'v'

	return words,weights

def main():
	conn = sqlite3.connect('example.db')
	c = conn.cursor()

	c.execute("SELECT id, content from letters;")

	conn2 = sqlite3.connect('lingstats.db')
	c2 = conn2.cursor()
	c2.execute("CREATE TABLE IF NOT EXISTS termfreq (docID INT, word TEXT, freq INT, pos_tag TEXT)")

	termfreq = []
	dokfreq = Counter()
	for (id,letter) in c:
		print("\r", id)
		tok, tags = tokenizeCorpusWeighted(letter)
		#print(tok)
		termfreq=Counter(tok)
		#print(termfreq)

		for w in termfreq:
			c2.execute("INSERT INTO termfreq VALUES ( ? , ? , ? , ? )", (id, w, str(termfreq[w]), tags[w]))
		conn2.commit()




if __name__ == "__main__":
	main()