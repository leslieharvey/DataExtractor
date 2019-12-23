import datetime
from canvasapi import Canvas
import DataExtractor

# Details needed to access Canvas and the course
API_URL = 'https://ufl.instructure.com/'
API_KEY = '1016~40RIzLLTgT01gRVzfhbsvMFIPWWZZZY4KhPF3WfAiPWhdv9Gi2HAZMarQ6uR8oAR'
courseID = 378337

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Get a course object for this course
course = canvas.get_course(courseID)

# Use the quiz adjustment if needed (for 547944)
quiz_adjustment = datetime.timedelta(hours=4, minutes=20)
M2_adjustment = datetime.timedelta(hours=-4, minutes=-20)
M10_adjustment = datetime.timedelta(hours=9, minutes=50)

# NEED TO MAKE ADJUSTMENTS ACCURATE FOR ALL SECTIONS
# Run for all applicable sections
sections = course.get_sections()
for s in sections:
    if s.name[:9] == "COP2271-2":
        DataExtractor.extraction(course, s.id, quiz_adjustment, M2_adjustment, M10_adjustment)
