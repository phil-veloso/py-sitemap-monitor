import requests 	# Used to retrieve sitemail + send mail
import logging 		# Used to record errors

#----------------------------------------------------------------------

from config import config		# app configuration

#----------------------------------------------------------------------

logger 				= logging.getLogger('monitor')

#----------------------------------------------------------------------	

class Notifications:
	"""
	Notifications functions 
	"""

	def send(subject, body):
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
			logger.error( 'Failed : email_send - {0}'.format(e) )


# End Notifications Class
#----------------------------------------------------------------------
