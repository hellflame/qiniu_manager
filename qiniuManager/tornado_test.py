"""
    Local Test for the basic http
"""
import tornado.ioloop as ioloop
import tornado.web as web

router = []


class NormalHandle(web.RequestHandler):
    def get(self):
        self.write("this is a get message")

    def post(self):
        # print self.request.body
        print "I Got You"
        self.write(self.request.body)

router.append(('/', NormalHandle))
settings = {
    'debug': True,
    'autoreload': True,
    'serve_traceback': True,
}

app = web.Application(handlers=router, **settings)

if __name__ == '__main__':
    app.listen(5000, address='127.0.0.1')
    ioloop.IOLoop.current().start()



