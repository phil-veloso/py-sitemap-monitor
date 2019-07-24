import sqlite3		# Used to store data
import logging 		# Used to record errors

from logging.handlers import RotatingFileHandler # Used for log rotation

#----------------------------------------------------------------------

import config
import monitor

#----------------------------------------------------------------------

logger 			= logging.getLogger('monitor')

#----------------------------------------------------------------------
def create_connection(db_file):
	""" 
	create a database connection to the SQLite database
	"""
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Exception as e:
		logger.error( 'Failed : create_connection - {0}'.format(e) )

	return None


#----------------------------------------------------------------------
def create_table(conn, create_table_sql):
	""" 
	create a table
	"""
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Exception as e:
		logger.error( 'Failed : create_table - {0}'.format(e) )


#----------------------------------------------------------------------
def database_init():
	""" 
	Initialise database
	"""	
	database = config.DB_PATH

	domain_table_name = config.DOMAIN + '_sitemap'
	url_table_name = config.DOMAIN + '_url'
	
	sql_create_domain_table = 	'''CREATE TABLE IF NOT EXISTS {name} (
									id integer PRIMARY KEY,
									sitemap_url text NOT NULL,
									date_time integer NOT NULL,
									total_urls integer NOT NULL,
									successes integer,
									redirects integer,
									client_errors integer,
									server_errors integer,
									slowest real NOT NULL,
									average real NOT NULL,
									fastest real NOT NULL,
									total_ime real NOT NULL
									);'''.format(name=domain_table_name )
 
	sql_create_url_table = 	'''CREATE TABLE IF NOT EXISTS {name} (
								id integer PRIMARY KEY,
								sitemap_id integer,
								page_url text NOT NULL,
								status_code integer NOT NULL,
								load_time real NOT NULL,
								comment text,
								FOREIGN KEY (sitemap_id) REFERENCES {domain} (id)
								)'''.format(name=url_table_name, domain=domain_table_name )
 
    # create a database connection
	conn = create_connection(database)
	if conn is not None:
		# create domain table
		create_table(conn, sql_create_domain_table)
		# create url table
		create_table(conn, sql_create_url_table)
	else:
		logger.error( 'Failed : cannot create the database connection' )