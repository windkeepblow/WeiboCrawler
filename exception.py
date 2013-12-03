class CookieExpiredException(Exception):
	def __init__(self, info):
		Exception.__init__(self)
		self.info = info

class WriteInfoException(Exception):
	def __init__(self, info):
		Exception.__init__(self)
		self.info = info

class ParseInfoException(Exception):
	def __init__(self, info):
		Exception.__init__(self)
		self.info = info
