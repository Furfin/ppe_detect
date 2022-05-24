import cv2
from app import *
import unittest
from main import *

client = app.test_client()

<<<<<<< HEAD
=======


>>>>>>> 6ebe1574b3f0a8ba56f13a7527d0ef44ef1f625f
class TestMainClassInit(unittest.TestCase):
    
    def test_init(self):
        object = CVTrackThread("static/vid1.mp4",1,db,Track)
        self.assertIsInstance(object, CVTrackThread, "Thread object is initialized")

class TestWebApp(unittest.TestCase):
    
    def test_dbModel(self):
        object = Track(0,0,'')
        self.assertIsInstance(object, Track, "DB model object is initialized")
    
<<<<<<< HEAD
=======
    
>>>>>>> 6ebe1574b3f0a8ba56f13a7527d0ef44ef1f625f
    def test_get(self):
        resp = client.get("/")
        self.assertEqual(resp._status_code,200)

<<<<<<< HEAD
=======

>>>>>>> 6ebe1574b3f0a8ba56f13a7527d0ef44ef1f625f
if __name__ == '__main__':
    unittest.main()