from functools import reduce
from operator import add
from fca.context import Context
from fuzzy.fca.fuzzy_context import FuzzyContext


## Search result -> context
def getContextFromSR(documents, terms, relation, maxKeywords):
	keywords = [x['keywords'][:maxKeywords] for x in documents]
	keywords = [[y[0] for y in x] for x in keywords]
	keywords = sorted(list(set(terms + reduce(add, keywords, []))))
	
	sites = _selectColumn('url', documents)
	ids = _selectColumn('id', documents)
	
	table = _getTable(relation, ids, keywords)
	return Context(table, sites, keywords)

def getFuzzyContext(documents, terms, keywordsScoreTable, termFrequency):
	keywords = [x['keywords'] for x in documents]
	keywords = [[y[0] for y in x] for x in keywords]
	keywords = sorted(list(set(terms + reduce(add, keywords, []))))
	sites = _selectColumn('url', documents)
	ids = _selectColumn('id', documents)
	
	table = getFuzzyTable(keywordsScoreTable, ids, keywords, termFrequency, terms)
	
	fContext = FuzzyContext(table, sites, keywords)
	return fContext

def getFuzzyTable(keywordsScoreTable, objects, attributes, termFrequency, terms):
	table = []
	
	for keywordsLine, objID in zip(map(lambda x: keywordsScoreTable[x], objects), objects):
		line = []	
		
		for attr in attributes:	
			if attr in terms:
				line.append(termFrequency(attr, objID))
			else:		
				line.append(keywordsLine.get(attr, 0))
		table.append(line)
	
	return table
	
	
def _getTable(relation, ids, keywords):
	table = []
	
	for id in ids:
		line = []
		for keyword in keywords:
			line.append(relation(keyword, id))
		table.append(line)
		
	return table

def _selectColumn(name, table):
	return [x[name] for x in table]

## Context -> slf
def context2slf(context):
	text = ['[Lattice]']
	text.append(str(context.height))
	text.append(str(context.width))
	text.append('[Objects]')
	
	for obj in context.objects:
		text.append(obj)
		
	text.append('[Attributes]')
	
	for attr in context.attributes:
		text.append(attr)
		
	text.append('[relation]')
	
	for line in context.table:
		string = ''
		for value in line:
			string += '1 ' if value else '0 '
		text.append(string)
		
	return '\n'.join(text)