$ python3 -m venv ~/environments/uptime_monitor

$ source ~/environments/uptime_monitor/bin/activate

$ pip3 install -r requirements.txt

$ python3 monitor.py

TODO:

- Improve email notifications on script error: email_send('Script Error', e)
