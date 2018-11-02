from jinja2 import Markup
import time

class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")


    def render(self, format):
        #return self.timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp, format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)