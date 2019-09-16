"""
Checker functions 
"""

# Standard library imports
import time 
import queue
import threading
import statistics
import logging

# Local application imports
from . import config, helpers

#----------------------------------------------------------------------

class CheckUrl:

	data_array 		= []
	page_errors 	= []
	load_times 		= []

	start_time 		= 0
	finish_time		= 0

	successes 		= 0
	redirects 		= 0
	client_errors 	= 0
	server_errors 	= 0

	def __init__(self):
		self.log = logging.getLogger('monitor')


	def check_url(self, q):
		#----------------------------------------------------------------------
		# Request url
		# @param: q - 
		# TODO: what to do if redirect?
		# TODO: what if connection refused? Flag
		#----------------------------------------------------------------------
		try: 

			while True:
				url = q.get()
				r = helpers.Helper().get_request(url)
				
				if r is not False:

					# self.log.info('Link: %s' % url)
					# self.log.info('Status: %d' % r.status_code)
					# self.log.info('Reason: %s' % r.reason)
					# self.log.info('Speed: %f' % r.elapsed.total_seconds())

					if r.status_code != 200:
						self.report_url(url, r)
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
						'url'		: url,
						'status'	: r.status_code,
						'time' 		: float( "{0:.2f}".format( r.elapsed.total_seconds() ) ),
						'comment'	: r.reason
					}

					self.load_times.append(r.elapsed.total_seconds())
					self.data_array.append( item )
				
				else:
					self.report_url(url, r)

				q.task_done()

		except Exception as e:
			self.log.error( 'Failed : check_url - {0}'.format(e) )


	def report_url(self, url, r):
		#----------------------------------------------------------------------
		# Record url error w/o statuc code 200
		# @param: url - 
		# @param: r - 		
		#----------------------------------------------------------------------
		try: 
			error = 'The url: {0} responded with an error ({1}): {2}'.format( url, r.status_code, r.reason )
			self.page_errors.append(error)
		except Exception as e:
			self.log.error( 'Failed : report_url - {0}'.format(e) )  


	def loop_urls(self, urls ):
		#----------------------------------------------------------------------
		# Loop urls - Multi-threading 
		# @param: urls - 
		#----------------------------------------------------------------------
		try: 

			q 			= queue.Queue(maxsize=0)
			threads		= 10

			start_time 	= time.time()

			for i in range(threads):
				worker = threading.Thread(target=self.check_url, args=(q,))
				worker.setDaemon(True)
				worker.start()

			for idx, url in enumerate(urls):
				q.put(url)
				if config.TEST_LOOP:
					if idx > 10:
						break

			q.join()

			finish_time = round( time.time() - start_time, 2)

		except Exception as e:
			self.log.error( 'Failed : loop_urls - {0}'.format(e) )

# End CheckUrl Class
#----------------------------------------------------------------------