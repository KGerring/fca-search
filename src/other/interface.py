from preprocess.index_manager import IndexManager
from other.constants import SETTINGS_FILE
from other.constants import DATABASES_FOLDER, DATA_FOLDER
from other.settings import Settings
from retrieval.search_engine import SearchEngine
from retrieval.index import Index
from fca_extension.fca_search_engine import FCASearchEngine
from other.data import getStopWords
from common.io import readfile
from common.string import createStem
from json import dumps, loads
from retrieval.temp_search import TempSearch

def tempSearch(path):
	content = readfile(path)
	data = loads(content);
	options = data.get('options', {})
	lang = options.get('lang', 'en')
	tempIndex = TempSearch()
	index = tempIndex.build(data, getStopWords(lang))
	res=tempSearchQuery(index, options.get('query', 'lion'), {}, lang)
	return getJson(res)

def getJson(searchResults, stopwatch = None):
	gen, sib, spec, meta, spellcheck, lattice = getFcaExt(searchResults)
	
	results = searchResults['origin']
	documents = results['documents']
	fca = {'gen':gen, 'spec':spec, 'sib':sib}
	if stopwatch:
		meta['time'] = stopwatch.total
	data = {'documents':documents, 'fca': fca, 'meta' : meta, 'spellcheck':spellcheck, 'lattice':lattice}
	jsonData = dumps(data)
	return jsonData

def tempSearchQuery(index, query, settings, lang):
	if not lang:
		lang = settings.get('lang')

	searchEngine = SearchEngine(index, getStopWords(lang))
	fca = FCASearchEngine(searchEngine, index, settings)
	searchResults = fca.search(query, lang)
	return searchResults

def getFcaExt(searchResults):
	spec = searchResults['specialization']
	gen = searchResults['generalization']
	sib = searchResults['siblings']
	meta = searchResults['meta']
	spellcheck = searchResults['suggestions']
	lattice = searchResults['lattice']
	
	return gen, sib, spec, meta, spellcheck, lattice

def searchQuery(databaseName, query, lang, stopwatch = None):
	index, settings = getIndexAndSettings(databaseName)
	if not lang:
		lang = settings.get('lang')

	searchEngine = SearchEngine(index, getStopWords(lang))
	fca = FCASearchEngine(searchEngine, index, settings)
	searchResults = fca.search(query, lang)
	return searchResults


def buildIndex(databaseName, linksSourcePath, currSettings, lang):
	settings = Settings(DATA_FOLDER + SETTINGS_FILE)
	for key, value in currSettings.items():
		settings.set(key, value)

	database = DATABASES_FOLDER + databaseName + '/'
	links = readfile(linksSourcePath).splitlines()
	indexManager = IndexManager(settings)
	indexManager.shutUp = False
	indexManager.build(links, database, getStopWords(lang), lang)

def findURL(databaseName, match):
	links = getAllLinks(databaseName)
	return [x for x in links if match in x]

def findDocID(databaseName, URLmatch):
	links = []
	for i, url in enumerate(getAllLinks(databaseName)):
		if URLmatch in url:
			links.append((url, i))
	return dict(links)

def documentFrequency(databaseName, word):
	return getIndex(databaseName).document_frequency(createStem(word, 'cs'))

def documentInfo(databaseName, docID):
	index = getIndex(databaseName)
	res = index.getDocInfo(int(docID))
	res['keywords'] = {index.stem2word(a) : b for a,b in res['keywords']}
	return res

def getWordCountInDoc(databaseName, word, docID):
	return getIndex(databaseName).getTermCountInDoc(createStem(word, 'cs'), int(docID))
	
def wordInDocFrequency(databaseName, word, docID):
	wordscount = documentInfo(databaseName, docID)['words']
	return getIndex(databaseName).term_frequency(createStem(word, 'cs'), int(docID), wordscount)

def wordFrequency(databaseName, word):
	return getIndex(databaseName).totalTermFrequency(createStem(word, 'cs'))

def getAllWords(databaseName):
	return getIndex(databaseName).getAllWords()

def getAllLinks(databaseName):
	index = getIndex(databaseName)
	return index.getLinks()

def getIndex(databaseName):
	return getIndexAndSettings(databaseName)[0]

def getIndexAndSettings(databaseName):
	database = DATABASES_FOLDER + databaseName + '/'
	settings = Settings(database + SETTINGS_FILE)
	index = Index(database, settings)
	return index, settings