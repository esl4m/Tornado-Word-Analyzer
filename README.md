# Tornado word analyzer
<br/>
Tornado is a Python web framework and asynchronous networking library.
<br/>
And this application is for analyzing custom url
 like (https://en.wikipedia.org/wiki/Main_Page) and counts the frequency of use of each word on that page.
<br/>
This application uses tornado, torndb, BeautifulSoup4 and pycrypto
<br/><br/>
To run this application on your local machine please follow these steps:
<br/>

* On your workspace create new folder 'tornado_analyzer' and in this folder create a new virtual environment<br/>
```
$ virtualenv env
```

* Then activate it :
```
$ source env/bin/activate
```

* Install requirements .. just run
```
$ pip install -r requirements.txt    # (to install all requirements)
```

* Clone latest version
```
$ git clone https://github.com/esl4m/Tornado-Word-Analyzer.git
```

* Create mysql Database :
<br/>
from terminal login to mysql
```
$ mysql --user=root --password=root
```
then create your database
```
$ create database hello_tornado ;
```
* Then import hello_tornado.sql
<br/>

* Run application :
```
$ python main.py
```
<br/>
To access the application .. type on your browser
```
localhost:8888
```
<br/><br/>