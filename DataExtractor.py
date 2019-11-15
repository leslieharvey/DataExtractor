# This will use data extraction tools to compile the desired data
# Created by Leslie Harvey

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
file = pd.read_excel(r'/Users/leslieharvey/Desktop/TestFile.xlsx')
for col in file:
    if col == "section":
        for index, row in file[col].iteritems():
            # Deletes the students not in the desired section
            if file[col][index] != "COP2271-29AD(13148)":
                file = file.drop(index)
            # Only keeps the students' first attempt
            else:
                if file["attempt"][index] != 1:
                    file = file.drop(index)

# Sorts the values according to their student id
file = file.sort_values(['sis_id'], ascending=True)

# Deletes the columns not needed
for col in file:
    if (col != "name") and (col != "sis_id") and (col != "submitted"):
        file = file.drop(columns=col)

file.to_excel("output.xlsx")
