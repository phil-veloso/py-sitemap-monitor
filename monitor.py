import re  # Used to get urls from html
import requests  # Used to retrieve sitemail + send mail

import queue  # Used to queue/limit no. of threads
import threading  # Used for multiprocessing of urls

import time # used for perforance reporting

import logging

logging.basicConfig(
		format='%(asctime)s - %(levelname)s : %(message)s', 
		filename='report.log',
		level=logging.INFO
	)


import credentials

# -----------
# Settings
# -----------

SITEMAP = 'https://www.veloso.com/xmlsitemap/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'}

# Log errors
errors = []

# -----------
# Functions
# -----------

# Fetch sitemap
def fetch_sitemap():
	try:
		r = requests.get( SITEMAP, headers=HEADERS ) 
		return r.content
	except Exception as e:
		logging.error( 'Failed : fetch_sitemap - {0}'.format(e) )


# Extract urls from sitemap html
def extract_urls(html):
	regex = '(?<=\<loc\>)(.*?)(?=\<\/loc\>)'
	try:
		page = str(html)
		return re.findall(regex, page)
	except Exception as e:
		logging.error( 'Failed : extract_urls - {0}'.format(e) )   


# Request url
def fetch_url(q):
	try: 
		while True:
			url = q.get()
			r = requests.get(url, headers=HEADERS) 
			if r.status_code != 200:
				report_url_error(url, r)
			# elif r.history:
				# report_url_redirect(url, r)
			logging.info('Link: %s' % url)
			logging.info('Status: %d' % r.status_code)
			logging.info('Reason: %s' % r.reason)
			logging.info('Speed: %f' % r.elapsed.total_seconds())
			q.task_done()
	except Exception as e:
		logging.error( 'Failed : fetch_url - {0}'.format(e) )


# Record url error w/o statuc code 200
def report_url_error(url, r):
	try: 
		global errors
		error = 'The url: {0} responded with an error ({1}): {2}'.format( url, r.status_code, r.reason )
		errors.append(error)
	except Exception as e:
		logging.warning( 'Failed : report_url_error - {0}'.format(e) )  


# Record url redirect
def report_url_redirect(url, r):
	try: 
		global errors
		error = 'The url: {0} was redirected to: {1}'.format(url,r.url)
		errors.append(error)
	except Exception as e:
		logging.warning( 'Failed : report_url_redirect - {0}'.format(e) )  


# Send report at end of cycle
def report_email(errors):
	try: 
		if len(errors) > 0:
			email_send('errors', errors)
		# else:
			# email_send('success', ['success']) 
	except Exception as e:
		logging.error( 'Failed : report_email - {0}'.format(e) )


# Send email w/ Mailgun
def email_send(subject, body):
	try:
		return requests.post(
			credentials.MAILGUN_URL,
			auth=('api', credentials.MAILGUN_KEY),
			data={
				'from': 'Notification <phil@my.inquisitive.solutions>',
				'to': ['phil@inquisitive.solutions'],
				'subject': subject,
				'text' : body
				}
			)
	except Exception as e:
		logging.error( 'Failed : email_send - {0}'.format(e) )

# -----------
# Execution
# -----------


logging.info('Start')
start = time.time()

html = fetch_sitemap()
logging.info('1: Fetched sitemap')

urls = extract_urls(html)
logging.info('2: Extracted URLs')

strt_loop = time.time()
logging.info('3: Start loop at {}s'.format(round(time.time() - start, 2)))
q = queue.Queue(maxsize=0)
num_threads = 10

for i in range(num_threads):
    worker = threading.Thread(target=fetch_url, args=(q,))
    worker.setDaemon(True)
    worker.start()

for idx, url in enumerate(urls):
    q.put(url)
    # if idx > 100:
    	# break

q.join()

logging.info('4: Finished loop in {}s'.format(round(time.time() - strt_loop, 2)))

report_email(errors)
logging.info('5: Report sent')

logging.info('Finish in: {}s'.format(round(time.time() - start, 2)))

