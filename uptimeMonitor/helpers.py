# Standard library imports
import os 			# used to create temp folder for log
import errno		# guard against race condition
import logging 		# Used to record errors

# Third party imports
import requests 	# Used to retrieve sitemail

# Local application imports
from . import config	

#----------------------------------------------------------------------

class Helper:
	"""
	Helper functions
	"""

	def __init__(self):
		self.log = logging.getLogger('monitor')

	def get_request(self, url):
		#----------------------------------------------------------------------
		# Send GET request.
		# @param: url - web address from request contents
		# @return: html string
		# TODO: chech return type is html
		#----------------------------------------------------------------------  
		try:		
			r = requests.get( url, headers=config.HEADERS ) 
			if r.status_code is not None:
				return r
			else:
				return False
		except Exception as e:
			self.log.error( 'Failed : send_request - {0}'.format(e) )
	
	
	def check_files_exists(self, file_path):
		#----------------------------------------------------------------------
		# Checks if log file exists else creates path
		# @param: file_path - system path for log file references in config file
		#----------------------------------------------------------------------
		if not os.path.exists(os.path.dirname( file_path )):
			try:
				os.makedirs(os.path.dirname( file_path ))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise


	def ascii_safe (self, string):
		#----------------------------------------------------------------------
		# Get ASCII string without raising encoding errors. 
		# @param : s - the Unicode string to be encoded
		# @return: encoded ASCII version of s, or None if s was None
		#----------------------------------------------------------------------
		try:
			if isinstance(string, unicode):
				s = string.encode('ascii', 'ignore')
			return s
		except Exception as e:
			self.log.error( 'Failed : send_request - {0}'.format(e) )
	

# End Helper Class
#----------------------------------------------------------------------
