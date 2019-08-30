import time 		# Used for perforance reporting
import statistics 	# importing the statistics module 

import logging 		# Used to record errors
import pdb			# add breakpoints - pdb.set_trace() 

#----------------------------------------------------------------------

from . import config 					# app configuration
from . import checker			
from . import database 		as dbm		# database related scripts
from . import notifications as email	# email functioanlity related scripts
from . import setup 					# create database and setup tables

#----------------------------------------------------------------------

logger 			= logging.getLogger('monitor')

#----------------------------------------------------------------------
def main():
	
	#--------
	# logger.info('Init')
	setup.Logger()	
	setup.CreateDatabase()

	#--------
	# logger.info('init DB connecton')
	database =	dbm.Database()

	#--------
	# logger.info('Checking domains in database')	
	has_domains = database.check_domains_exist()
	if has_domains is None:
		# logger.info('No domains found - adding list')	
		for i in config.DOMAINS:
			database.record_domain((i,))

	#--------
	# logger.info('Domains found - fetching sitemaps')
	sitemaps = database.fetch_sitemaps()

	#--------
	# logger.info('Loop sitemaps')
	for i in sitemaps:

		ckr = checker.Monitor()

		domain_id 	= i[0]
		sitemap_url	= i[1]	
	
		#--------
		# logger.info('2: Extracted URLs')
		urls = ckr.inspect_sitemap(sitemap_url)

		if urls is not None:

			date_time = time.time()

			#--------
			# logger.info('4: create sitemap entry' )
			siteloop_id = database.record_siteloop((domain_id, time.ctime(date_time), len(urls)))
			
			#--------
			# logger.info('5: Start loop at {}s'.format(round(time.time() - date_time, 2)))
			ckr.loop_urls( urls, siteloop_id )

			#--------	
			# logger.info('6: Record data items' )
			for i in ckr.data_array:	
				url_values = ( 
					i["seq_id"], 
					i["url"], 
					i["status"], 
					i["time"], 
					i["comment"]
				)	
				database.record_url( url_values )			

			#--------	
			# logger.info('7: Update sitemap entry' )
			slowest 		= float( "{0:.2f}".format( max(ckr.load_times) ) )
			average 		= float( "{0:.2f}".format( statistics.mean( ckr.load_times ) ) )
			fastest 		= float( "{0:.2f}".format( min(ckr.load_times ) ) )
			total_time 		= round( time.time() - date_time, 2)

			siteloop_values = (
				ckr.successes, 
				ckr.redirects, 
				ckr.client_errors, 
				ckr.server_errors, 
				slowest, 
				average, 
				fastest, 
				total_time )			

			database.update_siteloop(siteloop_id, siteloop_values)
		
			#--------
			# logger.info('8: Send report if errors')
			if len(ckr.page_errors) > 0:
				email.send('errors', ckr.page_errors)

	#--------
	# logger.info('Total time taken: {}s'.format(round(time.time() - date_time, 2)))
	database.close()

	
#----------------------------------------------------------------------
if __name__ == "__main__":
	main()