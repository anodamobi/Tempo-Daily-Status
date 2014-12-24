Tempo Daily Status
==================

Script that sends daily status email based on TEMPO Worklogs

Requirements:

* [Atlassian JIRA](https://www.atlassian.com/software/jira)
* [JIRA TEMPO plugin](http://www.tempoplugin.com)
* Python 2
* Python libs:
  * requests>=2.3.0
  * jinja2>=2.7

Installation
------------

1) Download latest source code archive or clone this repo to your server:

```
git clone https://github.com/anodamobi/Tempo-Daily-Status.git
```

2) Install all requirements

```
pip install -r requirements.txt
```

3) Copy `tds.conf.example` to `tds.conf` and edit it:

```
cp tds.conf.example tds.conf
nano tds.conf
```

4) Make test run

```
./tempo-daily-status.py
```


Usage
-----

Run it manually

```
./tempo-daily-status.py
```

or add it to your crontab (`crontab -e`)

```
0 18 * * * /home/user/Tempo-Daily-Status/tempo-daily-status.py
```

This will run the script everyday at 6 PM

Feedback & Contribution
-----------------------

Send your feedback and bugreports on [alex@anoda.mobi](mailto:alex@anoda.mobi) and GitHub issues.

Feel free to fork, update and submit pull-requests.