"""
InspectSitemap - 
"""

# Standard library imports
import re 
import time 
import logging 
import pdb			# add breakpoints - pdb.set_trace() 

# Third party imports
from bs4 import BeautifulSoup

# Local application imports
from .. import checker, helpers, config

#----------------------------------------------------------------------

LinkTags = {
    'a':        	[u'href'],
    'audio':    	[u'src'], # HTML5
    'body':     	[u'background'],
    'embed':    	[ u'src'],
    'frame':    	[u'src'],
    'head':     	[u'profile'],
    'html':     	[u'manifest'], # HTML5
    'iframe':   	[u'src' ],
    'img':      	[u'src', u'lowsrc', u'srcset', u'data-src'],
    'link':     	[u'href'],
    'meta':     	[u'href', u'content'],
    'script':   	[u'src'],
    'source':   	[u'src'], # HTML5
    'track':    	[u'src'], # HTML5
    'video':    	[u'src'], # HTML5
}

#----------------------------------------------------------------------

class InspectPageLinks():

	data 	= []
	errors	= []
	stats 	= []

	def __init__(self, url):
		
		self.log 	= logging.getLogger('monitor')
		urls 		= self.html_links(url)
		
		if urls is not None:

			ckr = checker.CheckUrl()

			ckr.loop_urls( urls )	

			self.data 			= ckr.data_array
			self.errors 		= ckr.page_errors
	
			self.stats = (
				time.ctime(ckr.start_time), 
				len(urls),
				ckr.successes, 
				ckr.redirects, 
				ckr.client_errors, 
				ckr.server_errors, 
				ckr.total_time )

		return


	def html_links(self, url):
		#----------------------------------------------------------------------
		# Extract http(s) links from page
		# @param: html - content of webpage as string
		# @return: list of urls 
		#----------------------------------------------------------------------		
		try:

			links 		= []
			false_links	= []

			if config.TEST_HTML:
				html 		= open("tests/webpage.html")
			else:
				r 			= helpers.Helper().get_request(url)
				page 		= r.content
				html		= str(page)

			soup = BeautifulSoup( html, 'html.parser')

			for tag in LinkTags:
				for link in soup.findAll( tag ):
					for attr in LinkTags[tag]:
						if link.get(attr) is not None:
							target_link = link.get(attr)
							if self.is_link(target_link):
								#print(target_link + "\n")
								links.append( target_link )
							else:
								false_links.append( target_link )

			if links is not None:
				return links
			else:
				self.log.error( 'Failed : find_html_links - no urls found ({0})'.format(e) )		

		except Exception as e:
			self.log.error( 'Failed : find_html_links - {0}'.format(e) )   		


	def is_link(self, url):
		#----------------------------------------------------------------------
		# Extract http(s) links from page
		# @param: html - content of webpage as string
		# @return: list of urls 
		# Ref: https://daringfireball.net/2010/07/improved_regex_for_matching_urls
		#----------------------------------------------------------------------			
		regex = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’]))'
		if re.search( regex, str(url) ):
			return True
		else:
			return False

# End InspectSitemap Class
#----------------------------------------------------------------------		

if __name__ == '__main__':
	InspectPageLinks()