# Standard library imports
import requests
import logging

# Local application imports
from . import config

#----------------------------------------------------------------------	

class Notifications:
	"""
	Notifications functions 
	"""

	def __init__(self):
		self.log = logging.getLogger('monitor')

	def send(self, subject, body):
		#----------------------------------------------------------------------		
		# Retrieve row count from domain table
		# @return: last row id
		#----------------------------------------------------------------------
		try:
			return requests.post(
				config.MAILGUN_URL,
				auth=('api', config.MAILGUN_KEY),
				data={
					'from': 'Notification <' +  config.MAILGUN_EMAIL + '>',
					'to': [config.NOTIFICATION_EMAIL],
					'subject': subject,
					'text' : body
					}
				)
		except Exception as e:
			self.log.error( 'Failed : email_send - {0}'.format(e) )


# End Notifications Class
#----------------------------------------------------------------------
