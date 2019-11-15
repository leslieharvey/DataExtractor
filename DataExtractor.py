# This will use data extraction tools to compile the desired data
# Created by Leslie Harvey

import os
import xlsxwriter
import pandas as pd


# # Creating the file
# data = xlsxwriter.Workbook("ExportedData.xlsx")
# dataSheet = data.add_worksheet("Data")
#
#
# dataSheet.write("A1", 'Test')
# data.close()
# --------------------------------------------------------------------


# Created function to process data changes
def modify_file(section, df):
    for col in df:
        if col == "section":
            for index, row in df[col].iteritems():
                # Deletes the students not in the desired section
                if df[col][index] != section:
                    df = df.drop(index)
                # Only keeps the students' first attempt
                else:
                    if df["attempt"][index] != 1:
                        df = df.drop(index)

    # Sorts the values according to their student id
    df = df.sort_values(['sis_id'], ascending=True)

    # Deletes the columns not needed
    for col in df:
        if (col != "name") and (col != "sis_id") and (col != "submitted"):
            df = df.drop(columns=col)

    return df


# Variables that will later be replaced with input functions
currentSection = "COP2271-29AD(13148)"
# Figure input
listBase = "M4 Quiz"

idList = ""
idCheck = False
# Accessing excel files stored in the project folder
path = os.getcwd() + "/Quizzes"
files = os.listdir(path)
quiz = {}
# Store all the valuable data in a dictionary
for f in files:
    finalPath = path + "/" + f
    label = f.split('.')[0]
    temp = pd.read_excel(finalPath)
    quiz[label] = modify_file(currentSection, temp)
    # Generating a list of all the students' id numbers
    if label == listBase:
        idList = quiz[label].iloc[:, 1]

# Verifies that the student ids match for each student
for fi in files:
    counter = 0
    index = 0
    fiCurrent = fi.split('.')[0]
    qCurrent = quiz[fiCurrent]
    length = len(idList)
    while index < length:
        if int(idList[index]) == qCurrent.iloc[counter, 1]:
            counter = counter + 1
            index = index + 1
        else:
            if int(idList[index+1]) != qCurrent.iloc[counter, 1] and index+1 < length:
                counter = counter + 1
                index = index - 1
            index = index + 1

file = pd.read_excel(r'/Users/leslieharvey/Desktop/TestFile.xlsx')
file.to_excel("output.xlsx", header=False, index=False)
