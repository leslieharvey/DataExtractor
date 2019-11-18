from canvasapi import Canvas
import datetime

# Details needed to access your school's Canvas, your Account, and your Course
API_URL = 'https://ufl.test.instructure.com/'
API_KEY = '1016~40RIzLLTgT01gRVzfhbsvMFIPWWZZZY4KhPF3WfAiPWhdv9Gi2HAZMarQ6uR8oAR'
courseID = 378337
section_num = ["000.UFL.2019-08-UF-0.13148"]

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Get a course object for this course
course = canvas.get_course(courseID)

# Get students for the specified section
enrollments = course.get_enrollments(type=["StudentEnrollment"], sis_section_id=section_num)
# Build a map of student ID to their name
idToName = dict((e.sis_user_id, e.user['name']) for e in enrollments)
# Build a map of Canvas ID to their student ID
# # idToCanvas = dict((e.user['id'], e.sis_user_id) for e in enrollments)
idToCanvas = {}
for e in enrollments:
    idToCanvas[e.user['id']] = {'canvas': e.user['id'], 'UF': e.sis_user_id}

# # Need to figure out how to get past attempt history
# assignment = course.get_assignment(3970170)
# submissions = assignment.get_submission(1028980, include="submission_history")
#
# print(type(submissions.submission_history))

# Searching for all of the homework assignments
assignments = course.get_assignments(search_term="HW:")
for a in assignments:
    print(a.name)
    # Due date of the assignment
    due_date = datetime.datetime.strptime(a.due_at, "%Y-%m-%dT%H:%M:%SZ")
    for s in a.get_submissions(include=["submission_history"]):
        try:
            # Only acting on students in specified section
            for person in idToCanvas:
                if s.user_id == person:
                    sub_date = datetime.datetime.strptime(s.submitted_at, "%Y-%m-%dT%H:%M:%SZ")
                    duration = due_date - sub_date
                    duration_seconds = duration.total_seconds()
                    hours = duration_seconds / 3600
                    idToCanvas[person].update({a.name: str(hours)})
                    # print(str(hours) + "   " + str(s.user_id))
        except:
            print("NaN for: " + str(person))
    print("\n")

print(idToCanvas)

