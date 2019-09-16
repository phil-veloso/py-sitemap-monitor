"""
Loop sitemaps in database, record responses and email errors
"""

# Standard library imports
import logging 
# import pdb			# add breakpoints - pdb.set_trace() 

# Local application imports
from .. import config, setup, database as dmb, notify
from ..inspector import sitemap as insp	

#----------------------------------------------------------------------

class MonitorSitemap:

	def __init__(self):
		self.logger = logging.getLogger('monitor')

		#--------
		print('Init')
		setup.SetupLogger()	
		setup.SetupDatabase()

		#--------
		print('init DB connecton')
		database =	dmb.Database()

		#--------
		print('Checking domains in database')	
		has_domains = database.check_domains_exist()
		if has_domains is None:
			print('No domains found - adding list')	
			for i in config.DOMAINS:
				database.record_domain((i,))

		#--------
		print('Domains found - fetching sitemaps')
		sitemaps = database.fetch_sitemaps()
		
		if sitemaps is not None:

			#--------
			print('Loop sitemaps')
			for i in sitemaps:

				domain_id 	= i[0]
				sitemap_url	= i[1]	
				
				inspector 	= insp.InspectSitemap(sitemap_url)

				stats 		= inspector.stats
				data 		= inspector.data
				errors		= inspector.errors

				list_stats = list(stats)
				list_stats.insert(0, domain_id)

				siteloop_id = database.record_siteloop(list_stats)

				for i in data:	
					url_values = ( 
						siteloop_id, 
						i["url"], 
						i["status"], 
						i["time"], 
						i["comment"]
					)
					database.record_url( url_values )			
			
				#--------
				print('8: Send report if errors')
				if len(errors) > 0:
					notify.Notifications().send('errors', errors)

		#--------
		print('END')
		database.close()


# End Monitor Class
#----------------------------------------------------------------------		

if __name__ == '__main__':
	MonitorSitemap()