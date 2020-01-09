import datetime
import xlsxwriter
from canvasapi import Canvas

# Details needed to access Canvas and the course
API_URL = 'https://ufl.instructure.com/'
API_KEY = '1016~40RIzLLTgT01gRVzfhbsvMFIPWWZZZY4KhPF3WfAiPWhdv9Gi2HAZMarQ6uR8oAR'
courseID = 378337

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Get a course object for this course
course = canvas.get_course(courseID)

# Get students for the specified section
enroll = course.get_enrollments(type=["StudentEnrollment"])
enrollments = []
for e in enroll:
    if e.course_section_id == 547944:  # Monday Morning section number
        enrollments.append(e)

# Build a map of Canvas ID to their student ID using a nested dictionary for Exams
idProject = {}
for e in enrollments:
    idProject[e.user['id']] = {'canvas': e.user['id'], 'name': e.user['name']}

# Compile all the information into an excel workbook
# ----------------------------------------------------
# Creating the file
data = xlsxwriter.Workbook("MondayMorning_Final_Project.xlsx")
sheetFinalProject = data.add_worksheet("Final Project")
cell_format = data.add_format({'bold': True, 'center_across': True})


def createMap(assignment, idStructure):
    # Due date of the assignment
    due_date = datetime.datetime.strptime(assignment.due_at, "%Y-%m-%dT%H:%M:%SZ")
    for s in assignment.get_submissions(include=["submission_history"]):
        # Only acting on students in specified section
        for person in idStructure:
            if s.user_id == person:
                sub_date = datetime.datetime.strptime(s.submitted_at, "%Y-%m-%dT%H:%M:%SZ")
                duration = due_date - sub_date
                duration_seconds = duration.total_seconds()
                hours = duration_seconds / 3600
                idStructure[person].update({"final_project": str(hours)})


def dataStorageFinalProject(idStructure, sheet):
    # Inputting the headers
    row = 0
    column = 0
    sheet.write(row, column, "Student Name", cell_format)
    column = column + 1
    sheet.write(row, column, "Canvas ID", cell_format)
    column = column + 1
    sheet.write(row, column, "Final Project", cell_format)
    # Writing each person and their associated data
    row = 1
    for person in idStructure:
        col = 0
        sheet.write(row, col, idStructure[person]['name'])
        col = col + 1
        sheet.write_number(row, col, int(idStructure[person]['canvas']))
        col = col + 1
        sheet.write_number(row, col, float(idStructure[person]['final_project']))
        row = row + 1
    sheet.set_column(0, row, 18)
    print("Final Project")


finalAssignment = course.get_assignment(3970154)
createMap(finalAssignment, idProject)
dataStorageFinalProject(idProject, sheetFinalProject)

# Saving the excel file
data.close()
