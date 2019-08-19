import re  			# Used to get urls from html
import requests 	# Used to retrieve sitemail
import queue 		# Used to queue/limit no. of threads
import threading 	# Used for multiprocessing of urls
import time 		# Used for perforance reporting
import statistics 	# importing the statistics module 

import logging 		# Used to record errors
from logging.handlers import RotatingFileHandler # Used for log rotation

import pdb			# add breakpoints - pdb.set_trace() 

#----------------------------------------------------------------------

import config 			# CUSTOM - APPLICATION Configuration
import database 		# CUSTOM - database related scripts
import notifications	# CUSTOM - email functioanlity related scripts
import helpers			# CUSTOM - helper functions

#----------------------------------------------------------------------

logger 			= logging.getLogger('monitor')

#----------------------------------------------------------------------

page_errors 	= []

successes 		= 0
redirects 		= 0
client_errors 	= 0
server_errors 	= 0

load_times 		= []
data_array 		= []

#----------------------------------------------------------------------
def logger_init():
	"""
	Initiaite Logging
	"""
	level = logging.WARNING

	helpers.check_exists( config.LOG_PATH )

	handler = RotatingFileHandler(
		config.LOG_PATH, 
		maxBytes=100*1024*100, 
		backupCount=5)

	formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')  
	handler.setFormatter(formatter)

	logger.setLevel(level)
	logger.addHandler(handler)

	logging.getLogger("re").setLevel(logging.WARNING)
	logging.getLogger("requests").setLevel(logging.WARNING) 
	logging.getLogger("queue").setLevel(logging.WARNING)
	logging.getLogger("threading").setLevel(logging.WARNING) 


#----------------------------------------------------------------------
def inspect_sitemap(url):
	"""
	Inspect sitemap for Urls
	"""
	sitemap 		= fetch_url(url)

	urls 			= []
	reg_sitemap 	= '(?<=\<sitemap\>)(.*?)(?=\<\/sitemap\>)'
	reg_url			= '(?<=\<url\>)(.*?)(?=\<\/url\>)'

	try:
		html 			= str(sitemap)

		site_submaps 	= re.findall(reg_sitemap, html)
		site_links 		= re.findall(reg_url, html)

		# extract urls found in sitemap
		if len(site_links) > 0:
			for i in site_links:
				url = extract_links(i)
				urls.append(url[0])

		# query submaps and extract urls
		if len(site_submaps) > 0 :
			for i in site_submaps:
				submap_link 	= extract_links(i)
				submap_page		= fetch_url(submap_link[0])
				submap_html		= str(submap_page)
				page_urls 			= extract_links( submap_html )
				if len( page_urls ) > 0:			
					for i in page_urls:
						urls.append(i)

		return urls

	except Exception as e:
		logger.error( 'Failed : inspect_sitemap - {0}'.format(e) )   


#----------------------------------------------------------------------
def fetch_url(url):
	"""
	Fetch sitemap
	"""
	try:
		r = requests.get( url, headers=config.HEADERS ) 
		return r.content
	except Exception as e:
		logger.error( 'Failed : fetch_url - {0}'.format(e) )


#----------------------------------------------------------------------
def extract_links(html):
	"""
	Extract urls
	"""
	regex_link 		= '(?<=\<loc\>)(.*?)(?=\<\/loc\>)'
	try:
		page = str(html)
		links = re.findall(regex_link, page)
		if links is not None:
			return links
		else:
			logger.error( 'Failed : extract_links - unable to extract urls ({0})'.format(e) )		
	except Exception as e:
		logger.error( 'Failed : extract_links - {0}'.format(e) )   


#----------------------------------------------------------------------
def loop_urls( urls, sitemap_id ):
	"""
	Loop urls
	"""
	q = queue.Queue(maxsize=0)
	num_threads = 10

	for i in range(num_threads):
		worker = threading.Thread(target=check_url, args=(q,sitemap_id))
		worker.setDaemon(True)
		worker.start()

	for idx, url in enumerate(urls):
		q.put(url)
		if config.TEST_LOOP:
			if idx > 10:
				break

	q.join()


#----------------------------------------------------------------------
def check_url(q, sitemap_id):
	"""
	Request url
	"""
	try: 
		while True:
			url = q.get()
			r = requests.get(url, headers=config.HEADERS) 
			
			if r.status_code != 200:
				report_url_error(url, r)
			# elif r.history:
				# report_url_redirect(url, r)
			
			http_code = int(str(r.status_code)[0])
			if http_code == 2:
				global successes 
				successes += 1
			elif http_code == 3: 
				global redirects
				redirects += 1
			elif http_code == 4:
				global client_errors 
				client_errors += 1
			elif http_code == 5:
				global server_errors 
				server_errors += 1

			item = {
				'seq_id'	: sitemap_id,
				'url'		: url,
				'status'	: r.status_code,
				'time' 		: float( "{0:.2f}".format( r.elapsed.total_seconds() ) ),
				'comment'	: r.reason
			}

			load_times.append(r.elapsed.total_seconds())
			
			data_array.append( item )
			
			# logger.info('Link: %s' % url)
			# logger.info('Status: %d' % r.status_code)
			# logger.info('Reason: %s' % r.reason)
			# logger.info('Speed: %f' % r.elapsed.total_seconds())

			q.task_done()

	except Exception as e:
		logger.error( 'Failed : check_url - {0}'.format(e) )


#----------------------------------------------------------------------
def report_url_error(url, r):
	"""
	Record url error w/o statuc code 200
	"""
	try: 
		global page_errors
		error = 'The url: {0} responded with an error ({1}): {2}'.format( url, r.status_code, r.reason )
		page_errors.append(error)
	except Exception as e:
		logger.warning( 'Failed : report_url_error - {0}'.format(e) )  


#----------------------------------------------------------------------
def report_url_redirect(url, r):
	"""
	Record url redirect
	"""
	try: 
		global page_errors
		error = 'The url: {0} was redirected to: {1}'.format(url,r.url)
		page_errors.append(error)
	except Exception as e:
		logger.warning( 'Failed : report_url_redirect - {0}'.format(e) )  


#----------------------------------------------------------------------
def record_data( data_array ):
	"""
	Record data array 
	"""
	for i in data_array:
		database.record_url( ( 
			i["seq_id"], 
			i["url"], 
			i["status"], 
			i["time"], 
			i["comment"]
		) )


#----------------------------------------------------------------------
def update_siteloop_entry(sitemap_id, date_time):
	"""
	Update siteloop entry with stats
	"""
	slowest 		= float( "{0:.2f}".format( max(load_times) ) )
	average 		= float( "{0:.2f}".format( statistics.mean( load_times ) ) )
	fastest 		= float( "{0:.2f}".format( min(load_times ) ) )
	total_time 		= round( time.time() - date_time, 2)

	sitemap_id 		= database.update_siteloop(sitemap_id, (successes, redirects, client_errors, server_errors, slowest, average, fastest, total_time ))


#----------------------------------------------------------------------
def main():

	date_time  		= time.time()
	
	#--------
	# logger.info('Init')
	logger_init()

	#--------
	# logger.info('Setup databases')	
	database.setup_database()

	#--------
	# logger.info('Checking domains in database')	
	has_domains = database.query_domains()

	if has_domains is None:
		# logger.info('No domains found - adding list')	
		for i in config.DOMAINS:
			database.record_domain((i,))			
	
	# logger.info('Domains found - fetching sitemaps')
	sitemaps = database.fetch_sitemaps() # return array of sitemaps

	#--------
	# logger.info('Loop sitemaps')
	for i in sitemaps:

		domain_id 	= i[0]
		sitemap_url	= i[1]	

		#--------
		# logger.info('2: Extracted URLs')
		urls = inspect_sitemap(sitemap_url)

		if urls is not None:
			#--------
			# logger.info('4: create sitemap entry' )
			sitemap_id 		= database.record_siteloop((domain_id, time.ctime(date_time), len(urls)))

			#--------
			# logger.info('5: Start loop at {}s'.format(round(time.time() - date_time, 2)))
			loop_urls( urls, sitemap_id )

			#--------	
			# logger.info('6: Record data items' )
			record_data( data_array )

			#--------	
			# logger.info('7: Update sitemap entry' )
			update_siteloop_entry(sitemap_id, date_time)

			#--------
			# logger.info('8: Send report if errors')
			if len(page_errors) > 0:
				notifications.email_send('errors', page_errors)
	
	# logger.info('Total time taken: {}s'.format(round(time.time() - date_time, 2)))

	
#----------------------------------------------------------------------
if __name__ == "__main__":
	main()