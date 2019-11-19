from canvasapi import Canvas
import datetime
import xlsxwriter

# Details needed to access Canvas and the course
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
# Build a map of Canvas ID to their student ID using a nested dictionary
idToCanvas = {}
for e in enrollments:
    idToCanvas[e.user['id']] = {'canvas': e.user['id'], 'UF': e.sis_user_id, 'name': e.user['name']}

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
                    # if s.user_id == 1027771:
                        # print(due_date)
                        # print(sub_date)
                        # print(duration)
                        # print(duration_seconds)
                        # print(hours)
        except:
            print("NaN for: " + str(person))
    print("\n")

# Compile all the information into an excel workbook
# ----------------------------------------------------
# Creating the file
data = xlsxwriter.Workbook("ExportedData.xlsx")
dataSheet = data.add_worksheet("HW Submission")
cell_format = data.add_format({'bold': True, 'center_across': True})

# Inputting the headers
row = 0
column = 0
dataSheet.write(row, column, "Student Name", cell_format)
column = column + 1
dataSheet.write(row, column, "UF ID", cell_format)
column = column + 1
dataSheet.write(row, column, "Canvas ID", cell_format)
column = column + 1
for a in assignments:
    label = a.name.split(':')[0]
    dataSheet.write(row, column, label, cell_format)
    column = column + 1

# Writing each person and their associated data
row = 1
for person in idToCanvas:
    col = 0
    dataSheet.write(row, col, idToCanvas[person]['name'])
    col = col + 1
    dataSheet.write_number(row, col, int(idToCanvas[person]['UF']))
    col = col + 1
    dataSheet.write_number(row, col, int(idToCanvas[person]['canvas']))
    for a in assignments:
        col = col + 1
        try:
            dataSheet.write_number(row, col, float(idToCanvas[person][a.name]))
        except:
            dataSheet.write(row, col, "NaN")
    row = row + 1

# Saving the excel file
dataSheet.set_column(0, row, 18)
data.close()
