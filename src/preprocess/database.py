from collections import Counter
from common.funcfun import lmap
from functools import reduce
from operator import add
from preprocess.words import get_words
from preprocess.html_remover import HTMLRemover
from common.string import normalize_text

def getinfo(documents):
	counters = list(enumerate(map(lambda x: Counter(x), documents)))
	allwords = reduce(add, documents)
	allwords_counter = Counter(allwords)
	words = sorted(set(allwords))
	occ = lmap(lambda x: ((x, allwords_counter[x]), occurences(counters, x)), words)
	return occ

def occurences(counters, word):
	return lmap(lambda x: (x[0], x[1][word]), filter(lambda x: word in x[1], counters))

def group(database, keylen = 1):
	dic = {}
	for record in database:
		key = record[0][0][:keylen]
		if key in dic:
			dic[key].append(record)
		else:
			dic[key] = [record]
	return dic

def compile_text(sites):
	htmlrem = HTMLRemover()
	sites = map(htmlrem.compile, sites)
	sites = map(normalize_text, sites)
	sites = map(get_words, sites)
	return group(getinfo(list(sites)))