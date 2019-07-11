$ python -m venv ~/Repo/url_monitor

$ source ~/Repo/url_monitor/bin/activate

$ pip install -r requirements.txt

$ python monitor.py

## Build
$ docker-compose build

## Run 
$ docker run [-detach] siteping:tag

# Access docker container
$ docker exec -it [containerID] /bin/sh