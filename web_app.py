import random
import threading
import time
import redis

from main import CVTrackThread

from flask import Flask,render_template,redirect,request



exporting_threads = {}
app = Flask(__name__)
app.debug = True


@app.route('/<int:thread_id>')
def progress(thread_id):
    global exporting_threads
    if exporting_threads[thread_id].frames != int(exporting_threads[thread_id].totalFrames):
        print(exporting_threads[thread_id].frames != int(exporting_threads[thread_id].totalFrames))
        return str(exporting_threads[thread_id].frames) + '/' + str(int(exporting_threads[thread_id].totalFrames))
    else:
        r = redis.Redis()
        data = ''
        for i in r.smembers("ids_"+str(thread_id)):
            data += "data_" +str(thread_id) + "_"+ i.decode('utf-8') + ':' + r.get("data_" +str(thread_id) + "_"+ i.decode('utf-8')).decode('utf-8') + '<br>'
        return data+'!'
        

@app.route('/')
def index():
   return render_template('upload.html')
	
@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
   global exporting_threads
   if request.method == 'POST':
      f = request.files['file']
      f.save('static/' + str(f.filename))
      index = random.randint(0, 10000)
      exporting_threads[index] = CVTrackThread('static/' + str(f.filename),index)
      exporting_threads[index].start()
      return redirect('/' + str(index))

		
if __name__ == '__main__':
   app.run(debug = True)
   
#Use js and github.pages
#update everything with js and request to server

"""
track = CVTrackThread("static/vid2.mp4",random.randint(0, 10000))

track.start()

while True:
    time.sleep(1)
    print(track.frames,track.totalFrames)
"""