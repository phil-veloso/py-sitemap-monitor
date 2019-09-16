# Standard library imports
import logging 		
from logging.handlers import RotatingFileHandler

# Third party imports
import sqlite3

# Local application imports
from . import config, helpers, database as dmb

#----------------------------------------------------------------------

class SetupLogger:
	"""
	Create log file and setup log rotation and 
	"""

	def __init__(self):
		self.log = logging.getLogger('monitor')
		self.logger_init()


	def logger_init(self):
		#----------------------------------------------------------------------
		# Initialise logging setup
		#----------------------------------------------------------------------

		level = logging.WARNING

		# Check if log exists else create
		helper = helpers.Helper()
		helper.check_files_exists( config.LOG_PATH )

		# setup log rotation
		handler = RotatingFileHandler(
			config.LOG_PATH, 
			maxBytes=100*1024*100, 
			backupCount=5)

		formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')  
		handler.setFormatter(formatter)

		self.log.setLevel(level)
		self.log.addHandler(handler)	


# End Logger Class
#----------------------------------------------------------------------

class SetupDatabase:
	"""
	Setup tables for recording domain sitemaps, sitemap loops and urls
	"""

	def __init__(self):
		self.log = logging.getLogger('monitor')

		# Initiate database
		database =	dmb.Database()

		# Connect to database 
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
					sitemap_url text NOT NULL
				);'''.format(
					name=dmb.Database().domain_table_name )

			self.cur.execute(sql)
		except Exception as e:
			self.log.error( 'Failed : create_domain_table - {0}'.format(e) )	


	def create_siteloop_table(self):
		#----------------------------------------------------------------------
		# Check if siteloop table exists else create table
		#----------------------------------------------------------------------
		try:

			sql = '''CREATE TABLE IF NOT EXISTS {name} (
					id integer PRIMARY KEY,
					domain_id integer NOT NULL,
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
					name=dmb.Database().siteloop_table_name, 
					table=dmb.Database().domain_table_name )

			self.cur.execute(sql)
		except Exception as e:
			self.log.error( 'Failed : create_siteloop_table - {0}'.format(e) )	


	def create_url_table(self):
		#----------------------------------------------------------------------
		# Check if url table exists else create table
		#----------------------------------------------------------------------
		try:		

			sql = '''CREATE TABLE IF NOT EXISTS {name} (
					id integer PRIMARY KEY,
					siteloop_id integer NOT NULL,
					page_url text NOT NULL,
					status_code integer NOT NULL,
					load_time real NOT NULL,
					comment text,
					FOREIGN KEY (siteloop_id) REFERENCES {table} (id)
				)'''.format(
					name=dmb.Database().url_table_name, 
					table=dmb.Database().siteloop_table_name )
								
			self.cur.execute(sql)
		except Exception as e:
			self.log.error( 'Failed : create_url_table - {0}'.format(e) )			


# End CreateDatabase Class
#----------------------------------------------------------------------