from fca_extension.utilities import getContextFromSR, context2slf,\
	getFuzzyContext
from fca.concept import Concept
from common.io import trySaveFile
from other.constants import DATA_FOLDER
from fuzzy.fca.fuzzy_concept import FuzzyConcept
from fuzzy.FuzzySet import FuzzySet
import math
class FCASearchEngine:
	def __init__(self, searchEngine, index):
		self.engine = searchEngine
		self.index = index
		self.maxDocs = 50
		self.stopwatch = None
		
	def search(self, query):
		originResults = self.engine.search(query)	
		terms = originResults['terms']		
		
		### Modify context
		modResult = self.engine.nostemSearch(' OR '.join(terms))
		
		modDoc, modTerms = self._getDocsAndTerms(modResult)
		modContext = getContextFromSR(modDoc, modTerms, self.index.contains_term)		
		
		
		modAttrsID = modContext.attrs2ids(terms)
		modSearchConcept = self._getSearchConceptByAttr(modContext, modAttrsID)
		upperN = modContext.upperNeighbors(modSearchConcept)
		generalization = self._getGeneralization(upperN, modContext, terms, modSearchConcept)
		
		lowerN = modContext.lowerNeighbors(modSearchConcept)
		modSpec = self._getSpecialization(lowerN, modContext, terms, modSearchConcept)
		
		siblings = set()
		left = self._getLower(upperN, modContext)
		if left:
			right = self._getUppers(lowerN, modContext)
			siblings = (left & right) - {modSearchConcept}
			
		rankedSibl = [{'rank': round(x.similarity(modSearchConcept), 3), 'words':x} for x in siblings]
		rankedSibl = sorted(rankedSibl, key=lambda x: x['rank'], reverse = True)
		self._translateIntents(rankedSibl, modContext)
		
#		trySaveFile(context2slf(modContext), DATA_FOLDER + 'context.slf')
		
#		test only
#		self.fuzzySearch(query, modContext.ids2attrs(modSearchConcept.intent))

		return {'origin':originResults, 'specialization':modSpec, 'generalization':generalization, 'siblings':rankedSibl}
	
	def fuzzySearch(self, query, debug = None):
		originResults = self.engine.search(query)	
		terms = originResults['terms']

		### Modify context
		modResult = self.engine.search(' OR '.join(terms))
		
		modDoc, modTerms = self._getDocsAndTerms(modResult)
		
		# fuzzy context
		fuzzyContext = getFuzzyContext(modDoc, modTerms, self.index.getKeywordsScore(), self.index.term_frequency)

#		fuzzyContext.setRoundMethod(lambda x: 0 if x == 0 else 1)
#		fuzzyContext.allValues = [0, 1]

		fuzzyContext.setRoundMethod(lambda x: 0 if x == 0 else (1 if x > 0.7 else 0.5))
		fuzzyContext.allValues = [0, 0.5, 1]

#		fuzzyContext.setRoundMethod(lambda x: math.ceil(x*10) / 10)
#		fuzzyContext.allValues = [x/10 for x in range(0, 11)]
		fuzzyContext.normalize()
		
		
		
		searchConcept = self._getFuzzySearchConceptByAttr(modTerms, fuzzyContext)
		
		print("Search concept:")
		print(searchConcept)
		
		upperN = fuzzyContext.upperNeighbors(searchConcept)
		lowerN = fuzzyContext.lowerNeighbors(searchConcept)
		left = self._getLower(upperN, fuzzyContext)
		
		print(fuzzyContext)
		specialization = self._getFuzzySpecialization(lowerN, fuzzyContext, terms, searchConcept)
		
#		print("Fuzzy context number: {0}".format(fuzzyContext.getFalseNumber()))
#		print("Fuzzy lower: {0}, Fuzzy upper: {1}".format(len(lowerN), len(upperN)))
#		print("Fuzzy left: " + str(len(left)))
		
		if left:
			right = self._getUppers(lowerN, fuzzyContext)	
#			testDebug = {frozenset({self.remLocalhost(x) for x in r.intent.keys()}) for r in right}
#			testDebug = {frozenset({self.remLocalhost(x) for x in r.intent.keys()}) for r in left}
			
			siblings = (left & right) - {searchConcept}
#			print(siblings)
#			print("-----------")
#			print(searchConcept)
#			print(len(siblings.remove(searchConcept)))
#			print("Fuzzy left: {0}, fuzzy right: {1}".format(len(left), len(right)))
#			print("Fuzzy siblings: {0}".format(len(siblings)))
#			print("------------------")
#		print("searchConcept: {0}".format(frozenset(debug) == frozenset(searchConcept.intent.keys())))
#		print(frozenset(debug))
#		print(frozenset(searchConcept.intent.keys()))
		
#		generalization = self._getGeneralization(upperN, modContext, terms, modSearchConcept)
#		
#		modLowerN = modContext.lowerNeighbors(modSearchConcept)
#		modSpec = self._getSpecialization(modLowerN, modContext, terms, modSearchConcept)

	def _getFuzzySpecialization(self, lower, context, terms, searchConcept):
		lowerN = [list(x.intent.support()) for x in lower]
		print(lowerN)
		
	def remLocalhost(self, url):
		return url.replace("http://localhost/matweb/", "")
		
	def _getFuzzySearchConceptByAttr(self, attrs, fuzzyContext):
		extent = fuzzyContext.down(FuzzySet({attr:1 for attr in attrs}))
		intent = fuzzyContext.up(extent)
		return FuzzyConcept(extent, intent)
	
	def _getUppers(self, concepts, context):
		upperN = set()
		for concept in concepts:
			upperN |= context.upperNeighbors(concept)
		return upperN
	
	def _getLower(self, concepts, context):
		lowerN = set()
		for concept in concepts:
			lowerN |= context.lowerNeighbors(concept)
		return lowerN
	
	def _getSpecialization(self, lowerN, context, terms, searchConcept):
		lowerN = {x.translate(context) for x in lowerN}		
		suggTerms = set(terms) | searchConcept.translate(context).intentNames
		specialization = [x.intentNames - suggTerms for x in lowerN]
		specialization = self._intents2words(specialization)
		rankedSpec = [{'words':list(x[0]), 'rank':len(x[1].extent)} for x in zip(specialization, lowerN)]
		rankedSpec = sorted(rankedSpec, key=lambda s: s['rank'], reverse=True)
		
		return rankedSpec
	
	def _translateIntents(self, concepts, context):
		for con in concepts:
			stems = con['words'].translate(context).intentNames
			con['words'] = [self.index.stem2word(stem) for stem in stems]
		
		#return [con.translate(context).intentNames for con in concepts]
	
	def _intents2words(self, concepts):
		return [{self.index.stem2word(stem) for stem in concept} for concept in concepts]
		
	
	def _getGeneralization(self, upperN, context, terms, searchConcept):
		upperN = {x.translate(context) for x in upperN}
		modSuggTerms = set(terms) | searchConcept.translate(context).intentNames
		
		rankedUpper = [{'rank':len(x.extent), 'words':x} for x in upperN]
		rankedUpper = sorted(rankedUpper, key=lambda x: x['rank'], reverse = True)
		
		for item in rankedUpper:
			intent = item['words'].intentNames
			stems = (modSuggTerms - intent) & set(terms)
			item['words'] = [self.index.stem2word(stem) for stem in stems]		
		
		
		generalization = [(modSuggTerms - x.intentNames) & set(terms)  for x in upperN]
		generalization = [{self.index.stem2word(stem) for stem in sugg} for sugg in generalization]
		return rankedUpper
	
	def _getDocsAndTerms(self, searchRes):
		return searchRes['documents'][:self.maxDocs], searchRes['terms']
	
	def _getUpperResults(self, originResults):
		terms = originResults['terms']
		query = ' OR '.join(terms)
		return self.engine.search(query)
	
	def _getSearchConcept(self, context, objects):
		sConcept = Concept()
		sConcept.intent = context.up(objects)
		sConcept.extent = context.down(sConcept.intent)
		return sConcept
	
	def _getSearchConceptByAttr(self, context, attributes):
		sConcept = Concept()
		sConcept.extent = context.down(attributes)
		sConcept.intent = context.up(sConcept.extent)
		return sConcept