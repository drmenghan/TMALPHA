__author__ = 'mhan0'

import xlrd
import time
import sys
import os
# XLSFile = "summary of vars good models.xlsx" #For Test
#Which file you want to analyze:
XLSFile = "summary of vars bad models.xlsx"
#Which sheet you want to analyze in the file:
sheet = 0



def get_time():
    """
    Get the current whole format time
    :return: String format time
    """
    result = ""
    from pytz import reference
    import datetime
    time = reference.LocalTimezone()

    from time import localtime, strftime
    result = strftime("%A, %d %B %Y %I:%M:%S %p ", localtime())

    result += time.tzname(datetime.datetime.now())
    return result



def get_sizeof_file(filename, suffix='B'):
    """
    Get size of one file, and output in the format with "K, M, G, T, P, etc."
    :param filename:
    :param suffix:
    :return:
    """
    num = os.stat(filename).st_size
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Tee(object):
    """
    For output both to log and std
    """
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)

#Analysis function:
def set_class(XLSFile, sheet):
    start_time = time.time()

    #Temperature result list:
    TermList = []
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
    return TermList
#Run the function
# set_class(XLSFile,sheet)

#Sort the result:
def get_counts(sequence):
    counts = {}
    for x in sequence:
        if x in counts:
            counts[x] +=1
        else:
            counts[x] = 1
    return counts


def get_filelist(mainDirectory, logfile):
    """
    Get list for specific Directory
    :param mainDirectory:
    :return:
    """
    #mainDirectory =str(mainDirectory)

    start_time = time.time()

    log = open(logfile, 'a')
    original = sys.stdout
    sys.stdout = Tee(sys.stdout, log)
    print("\nIndex files in ",mainDirectory,"\n---\t",get_time(),"\t---")
    result = []
    counter =0
    if not os.path.isdir(mainDirectory):
        print("---Illegal Directory! Check it again please!---")
    result = os.listdir(mainDirectory)
    for r in range(len(result)):
        result[r] = result[r].lower()


    print("Step 1: Finish the index of files name in folder", mainDirectory, ".")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    print("---\tThere are", len(result), "files in the folder.\t---\n\n")
    log.close()
    sys.stdout = original
    return result

def output_to_raw_data(Info,filename, logfile):
    """
    Output the string to raw data
    :param InfoList:
    :return: Joined result of raw data
    """
    # InfoList = list(Info)
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    f = open(filename,'w')
    RawContent = ""
    # for i in range(len(InfoList)):
    #     f.write(InfoList[i])
    #     print(len(InfoList)-i)
    w = open(filename,'w')
    for i in Info:
        mystr = str(i)+":   "+str(Info[i])
        w.writelines(str(mystr.encode('utf8', 'ignore')))
        w.writelines("")
        print(i,":\t",Info[i],"\n")
    w.close()
    sys.stdout = Tee(sys.stdout, log)
    print("Joined all content in the list to raw data done.", "\n---\t",get_time(),"\t---")
    print("---\tFile has already been output to file.",filename,"\t---")
    print("---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return RawContent



#
#Final result
#

def main():

    # XLSFile = "summary of vars good models.xlsx" #For Test
    #Which file you want to analyze:
    XLSFile = "summary of vars bad models.xlsx"
    #Which sheet you want to analyze in the file:
    sheet = 0
    #Temperature result list:
    TermList = []
    logfile = "CounterTermLog.txt"
    INPUTXLSFile = input("Which Excel File are you going to analyze?(Please include the .xlsx)\n")
    XLSFile = INPUTXLSFile
    SheetNum =0
    SheetNum = eval(input("Which sheet in the Excel File are you going to analyze?(0 for the first sheet)\n"))
    FileName = "Result.txt"
    FileName = input("Please input the output result file name?\n")
    TermList = set_class(XLSFile,SheetNum)
    CountsResult = get_counts(TermList)

    output_to_raw_data(CountsResult,FileName,logfile)






# from distutils.core import setup
# import py2exe
# setup(console=['CounterTerms.py'])





if __name__ == "__main__":
    main()
