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
currentSection = "COP2271-29AD(13148)"


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


file = modify_file(currentSection, file)

file.to_excel("output.xlsx")
