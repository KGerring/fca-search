from html.parser import HTMLParser

class HTMLRemover(HTMLParser):
	"Remove HTML tags, comments, and useless content like scripts or styles"
	
	def __init__(self):
		self.title = ''
		self.elementName = ''
		self.disabledElements = ['script', 'style']
		HTMLParser.__init__(self)
		
	def getText(self, html):
		self.reset()
		self.feed(html)
		return self.get_data()	
	
	def get_data(self):
		return ' '.join(self.puredata)
		
	def reset(self):
		self.description = ''
		self.title = ''
		self.elementName = ''
		self.puredata = []
		self.printp = True
		HTMLParser.reset(self)
	
	def handle_data(self, data):
		if self.elementName not in self.disabledElements:
			self.puredata.append(data)
		
		if self.elementName == 'title':
			if data.strip() and not self.title:
				self.title = data.strip()
				
		
	def handle_starttag(self, tag, attr):
		self.elementName = tag
		
		if tag == 'meta':
			attributes = dict(attr)
			name = attributes.get('name', '')
			if name.strip().lower() == "description":
				self.description = attributes.get('content', '')