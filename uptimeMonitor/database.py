"""
Database functions
"""

# Standard library imports
import logging

# Third party imports
import sqlite3

# Local application imports
from . import config

#----------------------------------------------------------------------

class Database: 

	domain_table_name 		= 'domains'
	siteloop_table_name 	= 'siteloops'
	url_table_name 			= 'urls'

	def __init__(self):
		self.log 	= logging.getLogger('monitor')	
		self.conn 	= self.open()
		self.cur 	= self.conn.cursor()

	def open(self):
		#----------------------------------------------------------------------
		# Open database connection
		# @return: initialised database connection
		#----------------------------------------------------------------------		
		try:
			self.conn = sqlite3.connect(config.DB_PATH)
			return self.conn
		except Exception as e:
			self.log.error( 'Failed : database open - {0}'.format(e) )


	def commit(self):
		#----------------------------------------------------------------------
		# Commit amendments to database
		#----------------------------------------------------------------------		
		try:
			self.conn.commit()
			return
		except Exception as e:
			self.log.error( 'Failed : database commit - {0}'.format(e) )
			

	def close(self):
		#----------------------------------------------------------------------
		# Close database connection
		#----------------------------------------------------------------------		
		try:
			self.conn.close()
			return
		except Exception as e:
			self.log.error( 'Failed : database close - {0}'.format(e) )


	def record_domain(self, values):
		#----------------------------------------------------------------------	
		# Create new database entry in domain table
		# @param: values - domain values to be recorded in database
		# TODO: sanitise values?
		#----------------------------------------------------------------------	
		try:	
			
			sql = ''' INSERT INTO {name} (
					sitemap_url
				)VALUES(?) '''.format(
					name=self.domain_table_name )
								
			self.cur.execute(sql, values)
			self.commit()
		except Exception as e:
			self.log.error( 'Failed : record_domain - {0}'.format(e) )


	def record_siteloop(self, values):
		#----------------------------------------------------------------------
		# Create new database entry in siteloop table
		# @param: values - siteloop values to be recorded
		# @return: last row id
		# TODO: sanitise values?
		#----------------------------------------------------------------------
		try:	

			sql = ''' INSERT INTO {name} (
					domain_id,
					date_time,
					total_urls,
					successes,
					redirects,
					client_errors,
					server_errors,
					slowest,
					average,
					fastest,
					total_time					
				)VALUES(?,?,?,?,?,?,?,?,?,?,?) '''.format(
					name=self.siteloop_table_name )

			self.cur.execute(sql, values)
			self.commit()
			row_id = self.cur.lastrowid
			return row_id			
		except Exception as e:
			self.log.error( 'Failed : record_siteloop - {0}'.format(e) )


	def record_url(self, values):
		#----------------------------------------------------------------------
		# Create new database entry in url table
		# @param: values - url values to be recorded
		# TODO: sanitise values?
		#----------------------------------------------------------------------
		try:		

			sql = ''' INSERT INTO {name} (
					siteloop_id,
					page_url,
					status_code,
					load_time,
					comment
				) VALUES(?,?,?,?,?) '''.format(
					name=self.url_table_name )

			self.cur.execute(sql, values)
			self.commit()
		except Exception as e:
			self.log.error( 'Failed : record_url - {0}'.format(e) )


	def update_siteloop(self, row_id, values):
		#----------------------------------------------------------------------
		# Update existing database entry in siteloop table
		# @param: siteloop_id - row id to be updated
		# @param: values - siteloop values to be recorded
		# TODO: sanitise values?
		#----------------------------------------------------------------------
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
				WHERE id = {id} '''.format(
					name=self.siteloop_table_name, 
					id=row_id )

			self.cur.execute(sql, values)
			self.commit()
		except Exception as e:
			self.log.error( 'Failed : update_siteloop - {0}'.format(e) )


	def check_domains_exist(self):
		#----------------------------------------------------------------------		
		# Retrieve row count from domain table
		# @return: last row id
		#----------------------------------------------------------------------
		try:

			sql = '''SELECT id FROM {name};'''.format( 
				name=self.domain_table_name )

			self.cur.execute(sql)
			row_count = self.cur.fetchone()
			return row_count
		except Exception as e:
			self.log.error( 'Failed : query_domains - {0}'.format(e) )


	def fetch_sitemaps(self):
		#----------------------------------------------------------------------
		# Retrieve all entries from domains table
		# @return: list of domain ids' and sitemap urls 
		#----------------------------------------------------------------------
		try:

			sql = '''SELECT id, sitemap_url FROM {name};'''.format( 
				name=self.domain_table_name )

			self.cur.execute(sql)			
			ids_and_urls = self.cur.fetchall()
			return ids_and_urls
		except Exception as e:
			self.log.error( 'Failed : fetch_sitemaps - {0}'.format(e) )


# End Database Class
#----------------------------------------------------------------------




