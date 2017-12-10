# botran
Attachments manager bot for Cisco Spark

[![Apache 2 licensed](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0)

## Presentation

Botran is a Cisco Spark bot initiative to improve the possibilities in terms of sharing files with a team in a specific and temporary way within a Cisco Spark space. This bot is not running in production and may not be available in Cisco Spark. The code allows to deploy such a bot.


## Getting Started

### Running a WSGI application

This version of Botran is working as a Flask application behind an Apache HTTP server. Make sure WSGI is enabled if you're using Apache or another web server and it is compatible with the version of Python used. Botran has been developped using Python 3.6 and not tested on other versions of Python 3. Also it is not compatible with Python 2.7.


### Example botran.conf for Apache 2, Ubuntu 14

```
<VirtualHost *:443>
...

  WSGIDaemonProcess botran user=botran group=botran threads=10 display-name=%{GROUP} queue-timeout=1000 socket-timeout=1000
  WSGIProcessGroup botran
  WSGIScriptAlias / /var/www/botran/botran.wsgi
...
</VirtualHost>
```


### Fill in your configuration file

Make sure to fulfill your own configuration file. To do it so, duplicate the example config file `default_settings_example.py` and rename it `default_settings.py`

### What about the webhook ?

Cisco Spark will shout events to the webhook URL that will be provided in the variable **BOTRAN_TARGET_URL**. If the webhook has not been created yet, Botran will take care of that for you.
