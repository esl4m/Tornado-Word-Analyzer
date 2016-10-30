# -*- coding: utf-8 -*-
from Crypto.Cipher import XOR
import base64
import urllib
# import tornado.httpserver
import tornado.ioloop
import tornado.web
import logging
import os.path
import torndb
from bs4 import BeautifulSoup
from collections import Counter
import re
import tornado.options
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="hello_tornado", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="root", help="database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/home/(.*)", WebHandler),
            (r"/get_data", GetDataHandler),
            (r"/add_url", URLHandler)
        ]
        settings = dict(
            app_title=u"Recipe Planner",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #xsrf_cookies=False,
            cookie_secret="11oETzKXQAGaYdkL5gEmGeFJJuYh7EQnp2XdTP1o/Vo=",
            login_url="/"            
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(BaseHandler):
    def get(self):
        print "loading started"
        self.render("index.html")


class WebHandler(BaseHandler):
    def get(self, page):
        print("rendering ", page)
        self.render(page)

    def post(self, page):
        print("rendering ", page)
        self.render(page)


class URLHandler(BaseHandler):
    def post(self):
        print "sending data to database"
        page_url = self.get_argument('page_url')

        print('Page url', page_url)
        # Download the content
        link = urllib.urlopen(page_url)
        htmlSource = link.read()
        link.close()

        soup = BeautifulSoup(htmlSource)
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip("\r\n...,/") for line in lines for phrase in line.split("  "))
        # drop blank lines
        result = '\n'.join(chunk for chunk in chunks if chunk)
        result = result.encode('utf-8')

        words = result.split()
        word_count = Counter(words)
        prepositions = ['a', 'de', 'do', 'da', 'of', 'by', 'an', 'on', 'in', 'is', 'it', 'to', 'st.', 'the', 'and',
                        'are', 'was', 'that', 'this', 'than', 'them', 'were', 'with', 'more', 'from']
        for i in word_count.keys():
            if i.lower() in prepositions:
                word_count.pop(i)

        # encode word #
        secret_key = '1234567890123456'  # create new & store somewhere safe
        cipher = XOR.new(secret_key)

        print("The Top {0} words".format(100))
        for word, count in word_count.most_common(100):
            # print("{0}: {1}".format(word, count))
            self.db.execute(
                "INSERT INTO words (word, no_of_repeats)"
                "VALUES (%s, %s)"
                "ON DUPLICATE KEY UPDATE word=VALUES(word), no_of_repeats=VALUES(no_of_repeats)",
                base64.b64encode(cipher.encrypt(word)), count
            )
        logging.info("inserted successfully")
        self.write("URL Added successfully")
        self.redirect("/home/index.html")


class GetDataHandler(BaseHandler):
    def get(self):
        print "Data"
        query = self.db.query("SELECT word, no_of_repeats FROM words")
        if not query:
            logging.info("No Data yet !")
            self.redirect("/home/index.html")
        else:
            logging.info("done")
            # encode word #
            secret_key = '1234567890123456'  # create new & store somewhere safe
            cipher = XOR.new(secret_key)

            data = []
            for words in self.db.query("SELECT * FROM words"):
                word_data = cipher.decrypt(base64.b64decode(words.word))
                no_of_repeats = words.no_of_repeats
                data.append((word_data, no_of_repeats))
            # self.finish({'Data': data})
            self.render("admin.html", data=data)


def main():
    print("Server running .. ")
    tornado.options.parse_command_line()
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    # http_server = tornado.httpserver.HTTPServer(Application())
    # http_server.listen(options.port)
    # tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
