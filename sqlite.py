import sqlite3		# Used to store data
import logging 		# Used to record errors

from logging.handlers import RotatingFileHandler # Used for log rotation

#----------------------------------------------------------------------

import config
import monitor

#----------------------------------------------------------------------

logger 			= logging.getLogger('monitor')

#----------------------------------------------------------------------
def init_database(timeStamp):
	"""
	Initiaite Database
	"""
	try:
		conn = sqlite3.connect('database.db')
		c = conn.cursor()

		c.execute('''CREATE TABLE ''' + config.DOMAIN + '''_sitemap (
						sequenceNo INTEGER,
						sitemap TEXT,
						dateTime INTEGER,
						totalUrls INTEGER,
						2xxResponses INTEGER,
						3xxResponses INTEGER,
						4xxResponses INTEGER,
						5xxResponses INTEGER,
						slowest REAL,
						average REAL,
						fastest REAL,
						totalTime REAL
					)''')

		c.execute('''CREATE TABLE ''' + config.DOMAIN + '''_urls_''' + timeStamp + ''' (
			sequenceNo INTEGER,
			pageUrl TEXT,
			statusCode INTEGER,
			loadTime REAL,
			comment TEXT
		)''')

		conn.commit()
		conn.close()
	except Exception as e:
		logger.error( 'Failed : init_database - {0}'.format(e) )
		monitor.email_send('Script Error', e)



