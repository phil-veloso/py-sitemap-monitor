import os 			# used to create temp folder for log
import errno		# guard against race condition

def check_exists( file_path ):
	"""
	Fetch sitemap
	"""
	if not os.path.exists(os.path.dirname( file_path )):
		try:
			os.makedirs(os.path.dirname( file_path ))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise