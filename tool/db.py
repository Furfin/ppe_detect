from concurrent.futures import thread
from flask_sqlalchemy import SQLAlchemy

from flask import Flask,render_template,redirect,request, Response

        # Open a cursor to perform database operations


exporting_threads = {}
app = Flask(__name__)
app.debug = True
r = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@0.0.0.0:5432/postgres'
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
db.session.add(Track(0,1,'2884337'))
db.session.add(Track(0,0,'2884337'))
db.session.commit()

for track in Track.query.filter_by(thread_id = 0):
        print(track.data)

