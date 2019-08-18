import sqlite3		# Used to store data
import logging 		# Used to record errors

import pandas as pd

from logging.handlers import RotatingFileHandler # Used for log rotation

logger 				= logging.getLogger('monitor')

#----------------------------------------------------------------------

import config
import monitor

#----------------------------------------------------------------------

domain_table_name 		= 'domains'
siteloop_table_name 	= 'siteloops'
url_table_name 			= 'urls'

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
def setup_database():
	""" 
	Initialise databases - domain, siteloop, urls
	"""		
	create_domain_table = 	'''CREATE TABLE IF NOT EXISTS {name} (
									id integer PRIMARY KEY,
									sitemap_url text NOT NULL,
									admin_email text
								);'''.format(name=domain_table_name )

	create_siteloop_table = 	'''CREATE TABLE IF NOT EXISTS {name} (
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
								);'''.format(name=siteloop_table_name, table=domain_table_name )
 
	create_url_table = 	'''CREATE TABLE IF NOT EXISTS {name} (
								id integer PRIMARY KEY,
								siteloop_id integer,
								page_url text NOT NULL,
								status_code integer NOT NULL,
								load_time real NOT NULL,
								comment text,
								FOREIGN KEY (siteloop_id) REFERENCES {table} (id)
							)'''.format(name=url_table_name, table=siteloop_table_name )
 
	conn = create_connection(config.DB_PATH)
	if conn is not None:

		# create domain table
		try: 
			create_table(conn, create_domain_table)
		except Exception as e:
			logger.error( 'Failed : create_domain_table - {0}'.format(e) )	

		# create siteloop table
		try:
			create_table(conn, create_siteloop_table)
		except Exception as e:
			logger.error( 'Failed : create_siteloop_table - {0}'.format(e) )	

		# create url table
		try:
			create_table(conn, create_url_table)
		except Exception as e:
			logger.error( 'Failed : create_url_table - {0}'.format(e) )			

		conn.commit()
		conn.close()
	else:
		logger.error( 'Failed : database_init - cannot create the database connection' )


#----------------------------------------------------------------------
def record_domain(values):
	"""
	create domain record
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:	
			sql = ''' INSERT INTO {name} (
						sitemap_url
					)VALUES(?) '''.format(name=domain_table_name)
			cur = conn.cursor()
			cur.execute(sql, values)
			# row_id = cur.lastrowid
			conn.commit()
			conn.close()
			# return row_id
		except Exception as e:
			conn.close()
			logger.error( 'Failed : record_domain - {0}'.format(e) )
	else:
		logger.error( 'Failed : record_domain - cannot create the database connection' )


#----------------------------------------------------------------------
def record_siteloop(values):
	"""
	create sitemap record
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:	
			sql = ''' INSERT INTO {name} (
						domain_id,
						date_time,
						total_urls
					)VALUES(?,?,?) '''.format(name=siteloop_table_name)
			cur = conn.cursor()
			cur.execute(sql, values)
			row_id = cur.lastrowid
			conn.commit()
			conn.close()
			return row_id
		except Exception as e:
			conn.close()
			logger.error( 'Failed : record_siteloop - {0}'.format(e) )
	else:
		logger.error( 'Failed : record_siteloop - cannot create the database connection' )


#----------------------------------------------------------------------
def record_url(values):
	"""
	create a new url record
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:
			sql = ''' INSERT INTO {name} (
							siteloop_id,
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


#----------------------------------------------------------------------
def update_siteloop(table_id, values):
	"""
	Update siteloop table 
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
						WHERE id = {id} '''.format(name=siteloop_table_name, id=table_id)
			cur = conn.cursor()
			cur.execute(sql, values)
			conn.commit()
			conn.close()
		except Exception as e:
			logger.error( 'Failed : update_siteloop - {0}'.format(e) )
	else:
		logger.error( 'Failed : update_siteloop - cannot create the database connection' )


#----------------------------------------------------------------------
def query_domains():
	"""
	Check whether domains exists in domain_table_name
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:
			sql = '''SELECT id FROM {name};'''.format( name=domain_table_name )
			cur = conn.cursor()
			cur.execute(sql)
			row_count = cur.fetchone()
			conn.close()
			return row_count
		except Exception as e:
			logger.error( 'Failed : query_domains - {0}'.format(e) )
	else:
		logger.error( 'Failed : query_domains - cannot create the database connection' )


#----------------------------------------------------------------------
def fetch_sitemaps():
	"""
	fetch_sitemaps
	"""
	conn = create_connection(config.DB_PATH)
	if conn is not None:
		try:
			sql = '''SELECT id, sitemap_url FROM {name};'''.format( name=domain_table_name )
			cur = conn.cursor()
			cur.execute(sql)			
			ids_and_urls = cur.fetchall()
			conn.close()
			return ids_and_urls
		except Exception as e:
			logger.error( 'Failed : fetch_sitemaps - {0}'.format(e) )
	else:
		logger.error( 'Failed : fetch_sitemaps - cannot create the database connection' )
	