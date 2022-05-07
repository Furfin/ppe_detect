from concurrent.futures import thread
from fileinput import filename
import random
import threading
import time
import cv2
from flask_sqlalchemy import SQLAlchemy
import os

from main import CVTrackThread
from PIL import Image

from flask import Flask,render_template,redirect,request, Response

        # Open a cursor to perform database operations


exporting_threads = {}
app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@db:5432/postgres"
db = SQLAlchemy(app)

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer,nullable=False)
    track_id = db.Column(db.Integer, nullable=False)
    data = db.Column(db.String(500), nullable=False)

    def __init__(self, thread_id, track_id,data):
        self.thread_id = thread_id
        self.track_id = track_id
        self.data = data

db.create_all()


@app.route('/data/<int:thread_id>')
def progress(thread_id):
    data = ''
    for track in Track.query.filter_by(thread_id = thread_id):
        data += str(track.data) + '</br>'
    return data+'!'

@app.route('/feed/<int:thread_id>')
def feed(thread_id):
        return Response(gen_frames(thread_id),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/<int:thread_id>')
def output(thread_id):
    return render_template('index.html',thread = thread_id)

def gen_frames(thread_id):
    while True:
        frame = exporting_threads[thread_id].img
        if frame == 0:
            break
        else:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
            yield frame
            yield b'\r\n\r\n'


@app.route('/')
def index():
   return render_template('upload.html')
	
@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
   global exporting_threads
   if request.method == 'POST':
      f = request.files['file']
      if f.filename.split(sep='.')[1] != "mp4":
          return "Invalid file extension! Try again"
      f.save('static/' + str(f.filename))
      index = random.randint(0, 10000)
      exporting_threads[index] = CVTrackThread('static/' + str(f.filename),index,db,Track)
      exporting_threads[index].start()
      return redirect('/' + str(index))

		
if __name__ == '__main__':
   app.run(debug = True)
   

"""
track = CVTrackThread("static/vid2.mp4",random.randint(0, 10000))

track.start()

while True:
    time.sleep(1)
    print(track.frames,track.totalFrames)
"""