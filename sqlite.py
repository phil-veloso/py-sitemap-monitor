import sqlite3		# Used to store data
import logging 		# Used to record errors

from logging.handlers import RotatingFileHandler # Used for log rotation

#----------------------------------------------------------------------

import config
import monitor

#----------------------------------------------------------------------

logger 				= logging.getLogger('monitor')

domain_table_name 	= config.DOMAIN + '_sitemap'
url_table_name 		= config.DOMAIN + '_url'

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
	sql_create_domain_table = 	'''CREATE TABLE IF NOT EXISTS {name} (
									id integer PRIMARY KEY,
									sitemap_url text NOT NULL,
									date_time integer NOT NULL,
									total_urls integer NOT NULL,
									successes integer,
									redirects integer,
									client_errors integer,
									server_errors integer,
									slowest real,
									average real,
									fastest real,
									total_time real
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
 
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		# create domain table
		create_table(conn, sql_create_domain_table)
		# create url table
		create_table(conn, sql_create_url_table)
		conn.commit()
		conn.close()
	else:
		logger.error( 'Failed : database_init - cannot create the database connection' )


#----------------------------------------------------------------------
def record_sitemap(values):
	"""
	create sitemap record
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:	
			sql = ''' INSERT INTO {name} (
						sitemap_url,
						date_time,
						total_urls
					)VALUES(?,?,?) '''.format(name=domain_table_name)
			cur = conn.cursor()
			cur.execute(sql, values)
			row_id = cur.lastrowid
			conn.commit()
			conn.close()
			return row_id
		except Exception as e:
			conn.close()
			logger.error( 'Failed : record_sitemap - {0}'.format(e) )
	else:
		logger.error( 'Failed : record_sitemap - cannot create the database connection' )


#----------------------------------------------------------------------
def update_sitemap(table_id, values):
	"""
	Update table 
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:
			sql = ''' UPDATE {name} SET 
						successes = ?,
						redirects = ?,
						client_errors = ?,
						server_errors = ?,
						slowest  = ?,
						average  = ?,
						fastest  = ?,
						total_time  = ?
						WHERE id = {id} '''.format(name=domain_table_name, id=table_id)
			cur = conn.cursor()
			cur.execute(sql, values)
			conn.commit()
			conn.close()
		except Exception as e:
			logger.error( 'Failed : update_sitemap - {0}'.format(e) )
	else:
		logger.error( 'Failed : update_sitemap - cannot create the database connection' )


#----------------------------------------------------------------------
def record_url(values):
	"""
	create a new url record
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:
			sql = ''' INSERT INTO {name} (
							sitemap_id,
							page_url,
							status_code,
							load_time,
							comment
							) VALUES(?,?,?,?,?) '''.format(name=url_table_name)

			cur = conn.cursor()
			cur.execute(sql, values)
			conn.commit()
			conn.close()
		except Exception as e:
			conn.close()
			logger.error( 'Failed : record_url - {0}'.format(e) )
	else:
		logger.error( 'Failed : record_url - cannot create the database connection' )
