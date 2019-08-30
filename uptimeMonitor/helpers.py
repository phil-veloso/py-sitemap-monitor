import os 			# used to create temp folder for log
import errno		# guard against race condition

class Helper:
	"""
	Helper functions
	"""

	def check_files_exists (file_path):
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


	def ascii_safe (string):
		#----------------------------------------------------------------------
		# Get ASCII string without raising encoding errors. 
		# @param : s - the Unicode string to be encoded
		# @return: encoded ASCII version of s, or None if s was None
		#----------------------------------------------------------------------
		if isinstance(string, unicode):
			s = string.encode('ascii', 'ignore')
		return s


# End Helper Class
#----------------------------------------------------------------------
