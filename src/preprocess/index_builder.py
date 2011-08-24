from collections import Counter
from common.funcfun import lmap, nothing
from functools import reduce
from operator import add
from preprocess.words import get_words, getstem
from preprocess.html_remover import HTMLRemover
from common.string import normalize_text
from retrieval.ranking import document_score

def getDocsStats(documents):
	counters = list(enumerate(map(lambda x: Counter(x), documents)))
	allwords = reduce(add, documents, [])
	allwords_counter = Counter(allwords)
	words = sorted(set(allwords))
	occurencesIndex = lmap(lambda x: ((x, allwords_counter[x]), occurences(counters, x)), words)
	wordscount = lmap(len, documents)
	return {'allwords' : allwords_counter, 'occurences' : occurencesIndex, 'wordscount' : wordscount}

def occurences(counters, word):
	return lmap(lambda x: (x[0], x[1][word]), filter(lambda x: word in x[1], counters))

def groupByKeylen(database, keylen):
	dic = {}
	for record in database:
		key = record[0][0][:keylen]
		if key in dic:
			dic[key].append(record)
		else:
			dic[key] = [record]
	return dic

def getKeywords(documents, index):
		keywords = []
		for docID, content in enumerate(documents):
			distContent = set(content)
			keyValues = {}
			for word in distContent:
				stem = getstem(word)
				keyValues[stem] = round(document_score([stem], docID, index), 5)
				
			foo = sorted(keyValues.items(), key=lambda x: x[1], reverse = True)
			keywords.append(foo)
		return keywords
	
def getDocumentsInfo(info):
	arr = []
	for url, wordscount, id, title in zip(info['urls'], info['wordscount'], range(len(info['urls'])), info['titles']):
		dic = {'url':url, 'wordscount':wordscount, 'id':id, 'title':title}
		arr.append(dic)
	return arr

def toIndex(documents, urls, stopwords, keylen, elapsed = nothing):
	htmlrem = HTMLRemover()
	parsedDocs = []
	correctUrl = []
	titles = []
	
	for site, url in zip(documents, urls):
		try:
			elapsed('parsing: ' + url)
			parsedDocs.append(get_words(normalize_text(htmlrem.compile(site)), stopwords))
			titles.append(htmlrem.title)
			correctUrl.append(url)
		except Exception as err:
			print('Cannot parse ' + str(url))
			print(str(err))
	
	elapsed('Collecting documents...')
	sitesStats = getDocsStats(parsedDocs)
	index = groupByKeylen(sitesStats['occurences'], keylen)
	
	return {'index': index, 'allwords':sitesStats['allwords'], 'urls': correctUrl, 'wordscount':sitesStats['wordscount'], 'parsedDocs':parsedDocs, 'titles':titles}