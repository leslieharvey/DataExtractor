from canvasapi import Canvas
import datetime
import xlsxwriter


def extraction(API_URL, API_KEY, courseID, section_ID, quiz_adjustment, M2_adjustment, M10_adjustment):
    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    # Get a course object for this course
    course = canvas.get_course(courseID)
    section = course.get_section(section_ID)
    section_name = section.name

    # Get students for the specified section
    enroll = course.get_enrollments(type=["StudentEnrollment"])
    enrollments = []
    for e in enroll:
        if e.course_section_id == section_ID:
            enrollments.append(e)

    # Build a map of Canvas ID to their student ID using a nested dictionary for HW
    idHW = {}
    for e in enrollments:
        idHW[e.user['id']] = {'canvas': e.user['id'], 'name': e.user['name']}
    assignmentsHW = course.get_assignments(includes=['overrides'], search_term="HW:")

    # Build a map of Canvas ID to their student ID using a nested dictionary for Quizzes
    idQuiz = {}
    for e in enrollments:
        idQuiz[e.user['id']] = {'canvas': e.user['id'], 'name': e.user['name']}
    assignmentsQuiz = course.get_assignments(includes=['overrides'], search_term="Quiz")

    # Build a map of Canvas ID to their student ID using a nested dictionary for Exams
    idExam = {}
    for e in enrollments:
        idExam[e.user['id']] = {'canvas': e.user['id'], 'name': e.user['name']}
    # Ensure that only exams are included in assignments
    groups = course.get_assignment_groups()
    for g in groups:
        if g.name == "Exams":
            examID = g.id
            break
    totalAssignments = course.get_assignments()
    exams = []
    for t in totalAssignments:
        if t.assignment_group_id == examID:
            exams.append(t.id)
    assignmentsExam = course.get_assignments(includes=['overrides'], assignment_ids=exams)

    # Build a map of Canvas ID to their student ID using a nested dictionary for Final Grades
    idFinalGrade = {}
    for e in enrollments:
        idFinalGrade[e.user['id']] = {'canvas': e.user['id'], 'name': e.user['name'], 'final_grade': e.grades['current_score']}

    # # Need to figure out how to get past attempt history
    # assignment = course.get_assignment(3970170)
    # submissions = assignment.get_submission(1028980, include="submission_history")
    #
    # print(type(submissions.submission_history))

    # Compile all the information into an excel workbook
    # ----------------------------------------------------
    # Creating the file
    data = xlsxwriter.Workbook(section_name + ".xlsx")
    sheetQuiz = data.add_worksheet("Quiz Submission")
    sheetHW = data.add_worksheet("HW Submission")
    sheetExam = data.add_worksheet("Exam Score")
    sheetFinalGrade = data.add_worksheet("Final Grade")
    cell_format = data.add_format({'bold': True, 'center_across': True})


    def createMap(assignments, idStructure, adjustment=None):
        # Searching for all of the homework assignments
        for a in assignments:
            print(a.name)
            # Due date of the assignment
            try:
                due_date = datetime.datetime.strptime(a.due_at, "%Y-%m-%dT%H:%M:%SZ")
                if adjustment is not None:
                    due_date -= quiz_adjustment
            # Except needed for when there are multiple due dates
            except:
                overrides = a.get_overrides()
                # Getting the override ID for the assignment
                for o in overrides:
                    if section_name in str(o):
                        num = str(o).split(") (")
                        override_ID = (num[1][:-1])
                override = a.get_override(override_ID)
                due_date = datetime.datetime.strptime(override.due_at, "%Y-%m-%dT%H:%M:%SZ")
                if adjustment is not None:
                    due_date -= quiz_adjustment
            for s in a.get_submissions(include=["submission_history"]):
                try:
                    # Only acting on students in specified section
                    for person in idStructure:
                        if s.user_id == person:
                            sub_date = datetime.datetime.strptime(s.submitted_at, "%Y-%m-%dT%H:%M:%SZ")
                            duration = due_date - sub_date
                            duration_seconds = duration.total_seconds()
                            hours = duration_seconds / 3600
                            idStructure[person].update({a.name: str(hours)})
                except:
                    print("NaN for: " + str(person))
            print("\n")


    # Fixing certain assignment due date differences
    def fixMap(assignments, idStructure, name, adjustment):
        for a in assignments:
            if a.name == name:
                print("Fixing " + a.name)
                for person in idStructure:
                    idStructure[person][a.name] = float(idStructure[person][a.name]) - (adjustment.total_seconds()/3600)
                print("\n")


    def dataStorage(assignments, idStructure, sheet):
        # Inputting the headers
        row = 0
        column = 0
        sheet.write(row, column, "Student Name", cell_format)
        column = column + 1
        sheet.write(row, column, "Canvas ID", cell_format)
        column = column + 1
        for a in assignments:
            label = a.name.split(':')[0]
            sheet.write(row, column, label, cell_format)
            column = column + 1

        # Writing each person and their associated data
        row = 1
        for person in idStructure:
            col = 0
            sheet.write(row, col, idStructure[person]['name'])
            col = col + 1
            sheet.write_number(row, col, int(idStructure[person]['canvas']))
            for a in assignments:
                col = col + 1
                try:
                    sheet.write_number(row, col, float(idStructure[person][a.name]))
                except:
                    sheet.write(row, col, "NaN")
            row = row + 1

        sheet.set_column(0, row, 18)


    def dataStorageFinalGrade(idStructure, sheet):
        # Inputting the headers
        row = 0
        column = 0
        sheet.write(row, column, "Student Name", cell_format)
        column = column + 1
        sheet.write(row, column, "Canvas ID", cell_format)
        column = column + 1
        sheet.write(row, column, "Final Grade", cell_format)
        # Writing each person and their associated data
        row = 1
        for person in idStructure:
            col = 0
            sheet.write(row, col, idStructure[person]['name'])
            col = col + 1
            sheet.write_number(row, col, int(idStructure[person]['canvas']))
            col = col + 1
            sheet.write_number(row, col, float(idStructure[person]['final_grade']))
            row = row + 1
        sheet.set_column(0, row, 18)
        print("Final Grade")

    def createMapExams(assignments, idStructure):
        # Searching for all of the Exams
        for a in assignments:
            print(a.name)
            for s in a.get_submissions(include=["submission_history"]):
                try:
                    # Only acting on students in specified section
                    for person in idStructure:
                        if s.user_id == person:
                            score = s.score
                            idStructure[person].update({a.name: str(score)})
                except:
                    print("NaN for: " + str(person))
            print("\n")

    # Create all the information maps
    createMap(assignmentsQuiz, idQuiz, quiz_adjustment)
    fixMap(assignmentsQuiz, idQuiz, "M2 Quiz: Input/Output", M2_adjustment)
    fixMap(assignmentsQuiz, idQuiz, "M10 Quiz: Images!", M10_adjustment)
    createMap(assignmentsHW, idHW)
    createMapExams(assignmentsExam, idExam)

    # Store all the information maps
    dataStorage(assignmentsQuiz, idQuiz, sheetQuiz)
    dataStorage(assignmentsHW, idHW, sheetHW)
    dataStorage(assignmentsExam, idExam, sheetExam)
    dataStorageFinalGrade(idFinalGrade, sheetFinalGrade)

    # Saving the excel file
    data.close()
