import random
import threading
import time

from flask import Flask


class ExportingThread(threading.Thread):
    def __init__(self):
        self.progress = 0
        super().__init__()

    def run(self):
        # Your exporting stuff goes here ...
        while True:
            time.sleep(1)
            self.progress += 10


exporting_threads = {}
app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    global exporting_threads

    thread_id = random.randint(0, 10000)
    exporting_threads[thread_id] = ExportingThread()
    exporting_threads[thread_id].start()

    return 'task id: #%s' % thread_id


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global exporting_threads

    return str(exporting_threads[thread_id].progress)
      
		
if __name__ == '__main__':
   app.run() 
   
   
#Use js and github.pages
#update everything with js and request to server