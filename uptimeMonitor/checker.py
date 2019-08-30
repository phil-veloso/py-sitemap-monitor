import re  			# Used to get urls from html
import requests 	# Used to retrieve sitemail
import queue 		# Used to queue/limit no. of threads
import threading 	# Used for multiprocessing of urls
import time 		# Used for perforance reporting
import statistics 	# importing the statistics module 

import logging 		# Used to record errors

#----------------------------------------------------------------------

from . import config 					# app configuration

#----------------------------------------------------------------------

log 			= logging.getLogger('monitor')

#----------------------------------------------------------------------

class Monitor:
	"""
	Monitor functions 
	"""

	data_array 		= []
	page_errors 	= []
	load_times 		= []

	successes 		= 0
	redirects 		= 0
	client_errors 	= 0
	server_errors 	= 0

	def send_request(self, url):
		#----------------------------------------------------------------------
		# Send GET request.
		# @param: url - web address from request contents
		# @return: html string
		# TODO: chech return type is html
		#----------------------------------------------------------------------  
		try:		
			r = requests.get( url, headers=config.HEADERS ) 
			return r.content
		except Exception as e:
			log.error( 'Failed : send_request - {0}'.format(e) )


	def inspect_sitemap(self, url):
		#----------------------------------------------------------------------
		# Extract urls found in sitemap and follow to submaps e.g. SEO Yoast
		# @param: url - web address of sitemap
		# @return: list of urls
		# TODO - set search depth 
		# TODO - set sub_map search as func inspect_sitemap
		#----------------------------------------------------------------------
		try:
			sitemap 		= self.send_request(url)
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
					url = self.find_xml_links(i)
					extracted_urls.append(url[0])

			# extract urls in site_submaps	
			if len(site_submaps) > 0 :
				for i in site_submaps:
					submap_link 	= self.find_xml_links(i)
					submap			= self.send_request(submap_link[0])
					submap_html		= str(submap)
					page_urls 		= self.find_xml_links(submap_html)
					if len( page_urls ) > 0:			
						for i in page_urls:
							extracted_urls.append(i)

			return extracted_urls

		except Exception as e:
			log.error( 'Failed : inspect_sitemap - {0}'.format(e) )   


	def find_xml_links(self, html):
		#----------------------------------------------------------------------
		# Extract XML links from page
		# @param: html - content of webpage as string
		# @return: list of urls 
		#----------------------------------------------------------------------		
		try:
			regex_link 		= '(?<=\<loc\>)(.*?)(?=\<\/loc\>)'
			links 			= re.findall(regex_link, html)

			if links is not None:
				return links
			else:
				log.error( 'Failed : find_xml_links - no urls found ({0})'.format(e) )		

		except Exception as e:
			log.error( 'Failed : find_xml_links - {0}'.format(e) )   


	def find_html_links(self, html):
		#----------------------------------------------------------------------
		# Extract http(s) links from page
		# @param: html - content of webpage as string
		# @return: list of urls 
		# TODO - Add regex for 
		#----------------------------------------------------------------------		
		try:
			regex_link 		= '(?<=\<loc\>)(.*?)(?=\<\/loc\>)'
			links 			= re.findall(regex_link, html)

			if links is not None:
				return links
			else:
				log.error( 'Failed : find_html_links - no urls found ({0})'.format(e) )		

		except Exception as e:
			log.error( 'Failed : find_html_links - {0}'.format(e) )   


	def loop_urls(self, urls, sitemap_id ):
		#----------------------------------------------------------------------
		# Loop urls - Multi-threading 
		# @param: urls - 
		# @param: sitemap_id - 
		#----------------------------------------------------------------------
		try: 

			q 		= queue.Queue(maxsize=0)
			threads	= 10

			for i in range(threads):
				worker = threading.Thread(target=self.check_url, args=(q,sitemap_id))
				worker.setDaemon(True)
				worker.start()

			for idx, url in enumerate(urls):
				q.put(url)
				if config.TEST_LOOP:
					if idx > 10:
						break

			q.join()

		except Exception as e:
			log.error( 'Failed : loop_urls - {0}'.format(e) )


	def check_url(self, q, sitemap_id):
		#----------------------------------------------------------------------
		# Request url
		# @param: q - 
		# @param: sitemap_id - 
		# TODO: what to do if redirect?
		#----------------------------------------------------------------------
		try: 

			while True:
				url = q.get()
				r = requests.get(url, headers=config.HEADERS) 
				
				# log.info('Link: %s' % url)
				# log.info('Status: %d' % r.status_code)
				# log.info('Reason: %s' % r.reason)
				# log.info('Speed: %f' % r.elapsed.total_seconds())

				if r.status_code != 200:
					self.report_url_error(url, r)
				# elif r.history:		
					# Do domething on redirect 			
				
				http_code = int(str(r.status_code)[0])
				if http_code == 2:
					self.successes += 1
				elif http_code == 3: 
					self.redirects += 1
				elif http_code == 4:
					self.client_errors += 1
				elif http_code == 5:
					self.server_errors += 1

				item = {
					'seq_id'	: sitemap_id,
					'url'		: url,
					'status'	: r.status_code,
					'time' 		: float( "{0:.2f}".format( r.elapsed.total_seconds() ) ),
					'comment'	: r.reason
				}

				self.load_times.append(r.elapsed.total_seconds())
				self.data_array.append( item )
				
				q.task_done()

		except Exception as e:
			log.error( 'Failed : check_url - {0}'.format(e) )


	def report_url_error(self, url, r):
		#----------------------------------------------------------------------
		# Record url error w/o statuc code 200
		# @param: url - 
		# @param: r - 		
		#----------------------------------------------------------------------
		try: 
			error = 'The url: {0} responded with an error ({1}): {2}'.format( url, r.status_code, r.reason )
			self.page_errors.append(error)
		except Exception as e:
			log.warning( 'Failed : report_url_error - {0}'.format(e) )  


# End Monitor Class
#----------------------------------------------------------------------