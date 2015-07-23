__author__ = 'mhan0'

import xlrd
import time
# XLSFile = "summary of vars good models.xlsx" #For Test
#Which file you want to analyze:
XLSFile = "summary of vars bad models.xlsx"
#Which sheet you want to analyze in the file:
sheet = 0
#Temperature result list:
TermList = []
#Analysis function:
def set_class(XLSFile, sheet):
    start_time = time.time()
    book = xlrd.open_workbook(XLSFile)
    sh = book.sheet_by_index(sheet)

    num_rows = sh.nrows
    num_cells = sh.ncols
    curr_row = 0
    # curr_cell = 0
    term = ''
    while curr_row < num_rows:
        curr_cell = 0
        while curr_cell < num_cells:
            if (len(str(sh.cell_value(curr_row, curr_cell)))>1 ):
                term = sh.cell_value(curr_row, curr_cell)
                TermList.append(term)
                print("Row:", curr_row,"Col:", curr_cell,"Value:", sh.cell_value(curr_row, curr_cell))
            curr_cell += 1
        curr_row += 1

    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    print("---\tThere are", len(TermList), "terms in the Excel.\t---")
#Run the function
set_class(XLSFile,sheet)

#Sort the result:
def get_counts(sequence):
    counts = {}
    for x in sequence:
        if x in counts:
            counts[x] +=1
        else:
            counts[x] = 1
    return counts

xx = get_counts(TermList)
#Final result
xx

from distutils.core import setup
# import py2exe
