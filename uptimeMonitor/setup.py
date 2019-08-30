import sqlite3		# Used to store data
import logging 		# Used to record errors
from logging.handlers import RotatingFileHandler # Used for log rotation

#----------------------------------------------------------------------	

from . import config 					# app configuration
from . import helpers as Helper		# helper functions
from . import database as Database	# database functions

#----------------------------------------------------------------------	

logger 	= logging.getLogger('monitor')

#----------------------------------------------------------------------

class Logger:
	
	def __init__(self):
		self.logger_init()


	def logger_init(self):
		#----------------------------------------------------------------------
		# Initialise logging setup
		#----------------------------------------------------------------------

		level = logging.WARNING
		
		# Check if log exists else create
		Helper.check_files_exists( config.LOG_PATH )

		# setup log rotation
		handler = RotatingFileHandler(
			config.LOG_PATH, 
			maxBytes=100*1024*100, 
			backupCount=5)

		formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')  
		handler.setFormatter(formatter)

		logger.setLevel(level)
		logger.addHandler(handler)	


# End Logger Class
#----------------------------------------------------------------------

class CreateDatabase:
	"""
	Setup tables for recording domain sitemaps, sitemap loops and urls
	"""

	def __init__(self):

		# Initiate & connec to database 
		database =	Database()
		self.conn = database.open()
		self.cur = self.conn.cursor()

		# Create tables
		self.create_domain_table()
		self.create_siteloop_table()
		self.create_url_table()
		
		# Close database connection
		database.close()


	def create_domain_table(self):	
		#----------------------------------------------------------------------
		# Check if domain table exists else create table
		#----------------------------------------------------------------------			
		try: 

			sql = '''CREATE TABLE IF NOT EXISTS {name} (
					id integer PRIMARY KEY,
					sitemap_url text NOT NULL,
					admin_email text
				);'''.format(
					name=Database.domain_table_name )

			self.cur.execute(sql)
		except Exception as e:
			logger.error( 'Failed : create_domain_table - {0}'.format(e) )	


	def create_siteloop_table(self):
		#----------------------------------------------------------------------
		# Check if siteloop table exists else create table
		#----------------------------------------------------------------------
		try:

			sql = '''CREATE TABLE IF NOT EXISTS {name} (
					id integer PRIMARY KEY,
					domain_id text NOT NULL,
					date_time integer NOT NULL,
					total_urls integer NOT NULL,
					successes integer,
					redirects integer,
					client_errors integer,
					server_errors integer,
					slowest real,
					average real,
					fastest real,
					total_time real,
					FOREIGN KEY (domain_id) REFERENCES {table} (id)
				);'''.format(
					name=Database.siteloop_table_name, 
					table=Database.domain_table_name )

			self.cur.execute(sql)
		except Exception as e:
			logger.error( 'Failed : create_siteloop_table - {0}'.format(e) )	


	def create_url_table(self):
		#----------------------------------------------------------------------
		# Check if url table exists else create table
		#----------------------------------------------------------------------
		try:		

			sql = '''CREATE TABLE IF NOT EXISTS {name} (
					id integer PRIMARY KEY,
					siteloop_id integer,
					page_url text NOT NULL,
					status_code integer NOT NULL,
					load_time real NOT NULL,
					comment text,
					FOREIGN KEY (siteloop_id) REFERENCES {table} (id)
				)'''.format(
					name=Database.url_table_name, 
					table=Database.siteloop_table_name )
								
			self.cur.execute(sql)
		except Exception as e:
			logger.error( 'Failed : create_url_table - {0}'.format(e) )			


# End CreateDatabase Class
#----------------------------------------------------------------------