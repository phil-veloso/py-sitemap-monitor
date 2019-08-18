import requests 	# Used to retrieve sitemail + send mail

import logging 		# Used to record errors
from logging.handlers import RotatingFileHandler # Used for log rotation

#----------------------------------------------------------------------

import config

#----------------------------------------------------------------------

logger 				= logging.getLogger('monitor')

#----------------------------------------------------------------------
def email_send(subject, body):
	"""
	Send email w/ Mailgun
	"""
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
