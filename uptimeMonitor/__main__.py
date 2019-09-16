"""
Loop sitemaps in database, record responses and email errors
"""

# Standard library imports
import argparse

from uptimemonitor.inspector.pagelinks import InspectPageLinks
from uptimemonitor.inspector.sitemap import InspectSitemap 

#----------------------------------------------------------------------

def main():

	parser = argparse.ArgumentParser(description='Process some integers.')

	parser.add_argument('url', help='target url for inspecitor')
	parser.add_argument('-s', '--sitemap', help='launch inspector for sitemap', action="store_true")
	parser.add_argument('-p', '--pagelinks', help='launch inspector for pagelinks', action="store_true")	

	args = parser.parse_args()

	if args.sitemap:
		# print("sitemap turned on")
		InspectSitemap(args.url)

	elif args.pagelinks:
		# print("pagelinks turned on")
		InspectPageLinks(args.url)

	print( args.url )

if __name__ == '__main__':
    main()

	