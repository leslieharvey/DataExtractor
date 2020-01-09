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

# Use the quiz adjustment if needed (for 547944 - 13148)
quiz_adjustment = datetime.timedelta(hours=4, minutes=20)  # pull back
M2_adjustment = datetime.timedelta(hours=-4, minutes=-20)  # push back
M10_adjustment = datetime.timedelta(hours=9, minutes=50)

# NEED TO MAKE ADJUSTMENTS ACCURATE FOR ALL SECTIONS
# Run for all applicable sections
sections = course.get_sections()
for s in sections:
    if s.name == "COP2271-29AD(13148)":
        DataExtractor.extraction(course, s.id, quiz_adjustment, M2_adjustment, M10_adjustment)
    elif s.name == "COP2271-29A4(13119)":
        zero = datetime.timedelta(hours=0, minutes=0)
        DataExtractor.extraction(course, s.id, zero, zero, M10_adjustment)
    elif s.name == "COP2271-29AH(13151)":
        time_delta = datetime.timedelta(hours=2, minutes=10)
        DataExtractor.extraction(course, s.id, time_delta, -time_delta, M10_adjustment)
