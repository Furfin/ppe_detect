import random
from flask_sqlalchemy import SQLAlchemy
from main import CVTrackThread
from flask import Flask,render_template,redirect,request, Response

exporting_threads = {}
app = Flask(__name__)
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

@app.route('/video/<thread_id>')
def video(thread_id):
    return render_template("index.html",thread_id = thread_id)

@app.route('/<int:thread_id>')
def output(thread_id):
    return Response(gen_data(thread_id))

def gen_data(thread_id):
    data = ''
    while True:
        new_data = exporting_threads[thread_id].datastring
        if new_data == "!": 
            break
        elif new_data != data and new_data != "":
            data = new_data
            yield data + "<br>"
    yield f"<a href = /video/{thread_id}>Video</a>"

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
      f.save("static/"+str(f.filename))
      index = random.randint(0, 10000)
      exporting_threads[index] = CVTrackThread('static/' + str(f.filename),index,db,Track)
      exporting_threads[index].start()
      return redirect('/' + str(index))

if __name__ == '__main__':
   app.run(debug = True)
