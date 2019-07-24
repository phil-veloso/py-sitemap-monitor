import re  			# Used to get urls from html
import requests 	# Used to retrieve sitemail + send mail
import queue 		# Used to queue/limit no. of threads
import threading 	# Used for multiprocessing of urls
import time 		# Used for perforance reporting
import logging 		# Used to record errors

from logging.handlers import RotatingFileHandler # Used for log rotation

#----------------------------------------------------------------------

import config 		# CUSTOM - APPLICATION Configuration
import sqlite 		# CUSTOM - APPLICATION Configuration

#----------------------------------------------------------------------

page_errors 	= []
logger 			= logging.getLogger('monitor')

#----------------------------------------------------------------------
def logger_init():
	"""
	Initiaite Logging
	"""
	level = logging.WARNING

	handler = RotatingFileHandler(
		config.LOG_PATH, 
		maxBytes=100*1024*100, 
		backupCount=5)

	formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')  
	handler.setFormatter(formatter)

	logger.setLevel(level)
	logger.addHandler(handler)

	logging.getLogger("re").setLevel(logging.WARNING)
	logging.getLogger("requests").setLevel(logging.WARNING) 
	logging.getLogger("queue").setLevel(logging.WARNING)
	logging.getLogger("threading").setLevel(logging.WARNING) 


#----------------------------------------------------------------------
def fetch_sitemap():
	"""
	Fetch sitemap
	"""
	try:
		r = requests.get( config.SITEMAP, headers=config.HEADERS ) 
		return r.content
	except Exception as e:
		logger.error( 'Failed : fetch_sitemap - {0}'.format(e) )
		email_send('Script Error', e)


#----------------------------------------------------------------------
def extract_urls(html):
	"""
	Extract urls from sitemap html
	"""
	regex = '(?<=\<loc\>)(.*?)(?=\<\/loc\>)'
	try:
		page = str(html)
		return re.findall(regex, page)
	except Exception as e:
		logger.error( 'Failed : extract_urls - {0}'.format(e) )   
		email_send('Script Error', e)


#----------------------------------------------------------------------
def fetch_url(q):
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
			logger.info('Link: %s' % url)
			logger.info('Status: %d' % r.status_code)
			logger.info('Reason: %s' % r.reason)
			logger.info('Speed: %f' % r.elapsed.total_seconds())
			q.task_done()
	except Exception as e:
		logger.error( 'Failed : fetch_url - {0}'.format(e) )
		email_send('Script Error', e)


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
		email_send('Script Error', e)


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
		email_send('Script Error', e)


#----------------------------------------------------------------------
def report_email(page_errors):
	"""
	Send report at end of cycle
	"""
	try: 
		if len(page_errors) > 0:
			email_send('errors', page_errors)
		# else:
			# email_send('success', ['success']) 
	except Exception as e:
		logger.error( 'Failed : report_email - {0}'.format(e) )
		email_send('Script Error', e)


#----------------------------------------------------------------------
def email_send(subject, body):
	"""
	Send email w/ Mailgun
	"""
	try:
		return requests.post(
			config.MAILGUN_URL,
			auth=('api', config.MAILGUN_KEY),
			data={
				'from': 'Notification <' +  config.MAILGUN_EMAIL + '>',
				'to': [config.NOTIFICATION_EMAIL],
				'subject': subject,
				'text' : body
				}
			)
	except Exception as e:
		logger.error( 'Failed : email_send - {0}'.format(e) )


#----------------------------------------------------------------------
def main():

	logger_init()
	sqlite.database_init()

	logger.info('Start')
	start = time.time()

	html = fetch_sitemap()
	logger.info('1: Fetched sitemap')

	urls = extract_urls(html)
	logger.info('2: Extracted URLs')

	strt_loop = time.time()
	logger.info('3: Start loop at {}s'.format(round(time.time() - start, 2)))

	"""
	START MULTI-THREADING
	"""
	q = queue.Queue(maxsize=0)
	num_threads = 10

	for i in range(num_threads):
		worker = threading.Thread(target=fetch_url, args=(q,))
		worker.setDaemon(True)
		worker.start()

	for idx, url in enumerate(urls):
		q.put(url)
		if config.TEST_LOOP:
			if idx > 100:
				break

	q.join()

	logger.info('4: Finished loop in {}s'.format(round(time.time() - strt_loop, 2)))

	report_email(page_errors)
	logger.info('5: Report sent')

	logger.info('Finish in: {}s'.format(round(time.time() - start, 2)))

#----------------------------------------------------------------------
if __name__ == "__main__":
	main()