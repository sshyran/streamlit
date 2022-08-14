import tornado
import asyncio

import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

async def start():
    app = make_app()
    app.listen(8888)
    print("sleep")
    await asyncio.sleep(10)

def main():
    asyncio.run(start())

if __name__ == "__main__":
    main()