"""
InspectSitemap - 
"""

# Standard library imports
import re 
import time 
import statistics 
import logging 

# Local application imports
from .. import checker, helpers

#----------------------------------------------------------------------

class InspectSitemap():

	data 	= []
	errors	= []
	stats 	= []

	def __init__(self, url):
		
		self.log 	= logging.getLogger('monitor')
		urls 		= self.inspect_links(url)
		
		if urls is not None:

			ckr = checker.CheckUrl()

			ckr.loop_urls( urls )	

			self.data 		= ckr.data_array
			self.errors 	= ckr.page_errors

			slowest 		= float( "{0:.2f}".format( max(ckr.load_times) ) )
			average 		= float( "{0:.2f}".format( statistics.mean( ckr.load_times ) ) )
			fastest 		= float( "{0:.2f}".format( min(ckr.load_times ) ) )
	
			self.stats = (
				time.ctime(ckr.start_time), 
				len(urls),
				ckr.successes, 
				ckr.redirects, 
				ckr.client_errors, 
				ckr.server_errors, 
				slowest, 
				average, 
				fastest, 
				ckr.finish_time )

		return


	def inspect_links(self, url):
		#----------------------------------------------------------------------
		# Extract urls found in sitemap and follow to submaps e.g. SEO Yoast
		# @param: url - web address of sitemap
		# @return: list of urls
		# TODO - set search depth 
		#----------------------------------------------------------------------
		try:
			r 				= helpers.Helper().get_request(url)
			sitemap 		= r.content
			sitemap_html	= str(sitemap)

			# query urls in sitemap
			reg_url			= '(?<=\<url\>)(.*?)(?=\<\/url\>)'
			site_links 		= re.findall(reg_url, sitemap_html)	

			# query submaps in sitemap
			reg_sitemap 	= '(?<=\<sitemap\>)(.*?)(?=\<\/sitemap\>)'
			site_submaps 	= re.findall(reg_sitemap, sitemap_html)		

			extracted_urls  = []

			# extract urls in sitemap	
			if len(site_links) > 0:
				for i in site_links:
					url = self.extract_links(i)
					extracted_urls.append(url[0])

			# extract urls in site_submaps	
			if len(site_submaps) > 0 :
				for i in site_submaps:
					submap 	= self.extract_links(i)
					urls 	= self.inspect_links(submap[0])
					extracted_urls = extracted_urls + urls
					
			return extracted_urls

		except Exception as e:
			self.log.error( 'Failed : inspect_sitemap - {0}'.format(e) )   


	def extract_links(self, xml):
		#----------------------------------------------------------------------
		# Extract XML links from page
		# @param: xml - content of webpage as string
		# @return: list of urls 
		#----------------------------------------------------------------------		
		try:
			regex_link 		= '(?<=\<loc\>)(.*?)(?=\<\/loc\>)'
			links 			= re.findall(regex_link, xml)

			if links is not None:
				return links
			else:
				self.log.error( 'Failed : extract_links - no urls found ({0})'.format(e) )		

		except Exception as e:
			self.log.error( 'Failed : extract_links - {0}'.format(e) )   	


# End InspectSitemap Class
#----------------------------------------------------------------------		

if __name__ == '__main__':
	InspectSitemap()