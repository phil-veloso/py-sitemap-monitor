$ python3 -m venv ~/environments/uptime_monitor

$ source ~/environments/uptime_monitor/bin/activate

$ pip3 install -r requirements.txt

$ python3 monitor.py



Table - Sitemap
	sequence number		- Primary Key
	Date/Time		
	total urls pings
	responses 2xx - success
	responses 3xx - redirect
	responses 4xx - client errors
	responses 5xx - server errors
	slowest page load
	average page load
	fastest page laod
	total time taken

Table - Urls
	sequence number 	- Secondary Key
	url 				- Primary Key
	status code
	load time
	comment