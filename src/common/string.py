import re
import unicodedata
import string
from common.funcfun import sreduce

def replace_single(text, strings, replacement):
	return re.sub('|'.join(map(re.escape, strings)), replacement, text)	

def replace_dict(text, dic):
	for k, v in dic.items():
		text = text.replace(k, v)
	return text

def sjoin(lst):
	return ''.join(map(str, lst))

def isletter(char):
	if strip_accents(char).lower() in string.ascii_lowercase:
		return char
	else:
		return False

def strip_accents(s):
	return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def replace_white_spaces(text, replace = ''):
	return re.sub('\s+', replace, text)

def remove_nonletters(text, replace = ''):
	return sjoin(map(lambda x: isletter(x) or replace, text))

def normalize_text(text):
	functions = [lambda x: remove_nonletters(x, ' '), lambda x: replace_white_spaces(x, ' '), lambda x: x.lower().strip()]
	return sreduce(functions, text)

def to_normal_lower(word):
	return strip_accents(word.lower().strip())