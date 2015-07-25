__author__ = 'mhan'
import os
import re
import sys
import xlrd
import time
import nltk
import pickle
import string
import datetime
import logging
import shutil
from difflib import SequenceMatcher
from dateutil.parser import parse
from bs4 import BeautifulSoup



class Statistic:
    """
    Summary final result
    """
    TotalMessage = 0                    #Total Message
    WithReply = 0                       #Message with Reply
    TotalUnanalyzable = 0               #All Unanalyzable Message
    NullMessage = 0                     #Message with no content
    AutoMessage = 0                     #Message created by mail software
    UndeliverableMessage = 0            #Message undeliverable
    CardRequestingMessage = 0           #Message request agreement
    WrongTransferMessage = 0            #Wrong by T Driver
    OtherNull = 0                       #Other Null

    def Outprint(self):
        print("The total number of raw messages is:", self.TotalMessage)
        print("-"*150)
        print("The total Unanalyzable message is:", self.TotalUnanalyzable)
        print("The total Null ERROR message is:",self.NullMessage)
        print("The total Auto ERROR message is:",self.AutoMessage)
        print("The total Undeliverable ERROR message is:",self.UndeliverableMessage)
        print("The total CardRequestingMessage ERROR message is:",self.CardRequestingMessage)
        print("The total WrongTransferMessage ERROR message is:",self.WrongTransferMessage)
        print("The total OtherNull ERROR is:",self.OtherNull)
        print("-"*150)
    def Outwrite(self):
        try:
             with open("Statistic.log",'w') as file:
                 file.write("The total number of raw messages is:"+ str(self.TotalMessage)+ "\n")
                 file.write("-"*150 + "\n")
                 file.write("The total Unanalyzable message is:" + str(self.TotalUnanalyzable) + "\n")
                 file.write("The total Null ERROR message is:" + str(self.NullMessage) + "\n")
                 file.write("The total Auto ERROR message is:" + str(self.AutoMessage) + "\n")
                 file.write("The total Undeliverable ERROR message is:" + str(self.UndeliverableMessage) + "\n")
                 file.write("The total CardRequestingMessage ERROR message is:" + str(self.CardRequestingMessage) + "\n")
                 file.write("The total WrongTransferMessage ERROR message is:" + str(self.WrongTransferMessage) + "\n")
                 file.write("The total OtherNull ERROR is:" + str(self.OtherNull) + "\n")
                 file.write("-"*150 + "\n")
        except:
            print("Can't open the file, check the input please!")


class Reply(object):
    """
    Defile the Reply in the WithReply Message
    """
    times = 0
    replyDates = []
    replyContents = []


class Message(object):
    """
    Define the message
    """

    AccountNumber = 0
    Name = ""
    Email = ""
    ZIPCODE = ""
    # Type = "X" #"X" for default, "E" for Email, "M" for Message, "U" for Unclassified
    Subject = "" #Kindes of Other, ERROR, NULL
    Content = ""
    SubjectFlag = False
    ReplyTimes = 0
    Reply = Reply()
    NullError = [False]*7 # For NullError Record
    CaseID = ""


class Question(object):
    """
    Defile Question in the Message
    """
    Level = 0
    QuestionNumber = 0
    QuestionContent = ""


class Tee(object):
    """
    For output both to log and std
    """
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)


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


def get_runtime(logfile):
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    print("\n---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()


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


def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_dic2(Dic):
    """
    Convert Dic to Dic2 for fiile operation
    :param Dic:
    :return:
    """
    Dic2 = Dic.replace("/","\\")
    # Dic2 = "\\" + Dic2
    return Dic2


def get_join_message(WithReplyList, WithoutReplyList, logfile):
    """
    Compare and join two kind of Message List
    :param WithReplyList:
    :param WithoutReplyList:
    :param logfile:
    :return:
    """

# MergeList = get_join_message(Message1, Message2, logfile)
# len(MergeList)
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    JoinList = []

    for withReply in WithReplyList:
        for withoutReply in  WithoutReplyList:
            if withReply.AccountNumber == withoutReply.AccountNumber:
                JoinList.append(withReply)
    sys.stdout = Tee(sys.stdout, log)
    print("\n---\t Merge",str(len(JoinList)),"message in total.\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    log.close()
    sys.stdout = original
    return JoinList


def fileCheck(srcDic, Dic, logfile):
    """
    Check the file by content and subject
    :param srcDic:
    :return: File operation to classify the messages
    """
    start_time = time.time()
    # Dic = "MoveTest/"
    # Dic2 = "MoveTest\\"
    # src = srcDic[1]
    ProcessingCounter = 0
    NumOfNullContentMessage = 0
    NumOfAutoMessage = 0
    NumOfCardRequestingMessage = 0
    NumOfUndeliverableMessage = 0
    NumOfWrongTransferMessage = 0
    # NumOfUnanalyzable = 0
    NumOfMessageWithReply = 0
    NumOfMessageWithoutReply = 0
    NumOfUnsolved = 0
    NumOfTotal = len(srcDic)

    #Percentage = NumOfTotal/100
    #sys.stdout = Tee(sys.stdout, log)
    original = sys.stdout
    log = open(logfile, 'a')
    Dic2 = get_dic2(Dic)
    sys.stdout = Tee(sys.stdout, log)
    print("\n---\tChecking files in ",Dic,"\t---","\n---\t",get_time(),"\t---")



    for filename in srcDic:
        file = Dic + filename
        # filename = src
        #file = Dic + src
        # filename = "content1801.txt"
        # file = "content1801.txt"
        sys.stdout = original
        ProcessingCounter+=1
        print("Checking file", filename, ", which is the",ProcessingCounter,"of", NumOfTotal, "files.")
        sys.stdout = Tee(sys.stdout, log)
        try:
            File = open(file,encoding="utf8")
            Text = str(File.readlines())
            File.close()

            if(len(Text)<50):
                DirName = Dic2 + "NullContentMessage\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfNullContentMessage += 1

            elif (re.search(r'.*This message was created automatically by mail delivery software.*', Text)):
                DirName = Dic2 + "AutoMessage\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfAutoMessage += 1

            elif (re.search(r'.*Card member .*\d{16}.* is requesting to have their Card Member Agreement sent to them.*', Text)):
                DirName = Dic2 + "CardRequestingMessage\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfCardRequestingMessage += 1

            elif (re.search(r'.*was undeliverable.*|.*was not delivered to.*', Text)):
                DirName = Dic2 + "UndeliverableMessage\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfUndeliverableMessage += 1

            elif (re.search(r'.*Per the Information Asset Classification Standard.*', Text)):
                DirName = Dic2 + "WrongTransferMessage\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfWrongTransferMessage += 1
            elif(re.search(r'.*Original Message.*', Text)):
                DirName = Dic2 + "MessageWithReply\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfMessageWithReply += 1
            else:
                pass
                DirName = Dic2 + "MessageWithoutReply\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + filename
                dst = DirName + filename
                shutil.move(src,dst)
                NumOfMessageWithoutReply += 1
        except:
            NumOfUnsolved += 1
            print("Cannot finish File check for file " + filename+ ", please recheck the file.")

        #Summary:

    NumOfUnanalyzable = NumOfNullContentMessage + NumOfAutoMessage + \
                        NumOfCardRequestingMessage + NumOfUndeliverableMessage + \
                        NumOfWrongTransferMessage

    print("Step 2: Finish checking of files in folder", Dic, ".")
    print("Summary:")
    print("NumOfNullContentMessage is:",NumOfNullContentMessage)
    print("NumOfAutoMessage is:",NumOfAutoMessage)
    print("NumOfCardRequestingMessage is:",NumOfCardRequestingMessage)
    print("NumOfUndeliverableMessage is:",NumOfUndeliverableMessage)
    print("NumOfWrongTransferMessage is:",NumOfWrongTransferMessage)
    print("NumOfUnanalyzable is:", NumOfUnanalyzable)
    print("NumOfUnsolved is:", NumOfUnsolved)

    print("---\tThere are",NumOfTotal- NumOfUnanalyzable - NumOfUnsolved,"of",NumOfTotal,"messages could be analyse.\t---")
    print("NumOfMessageWithoutReply is:", NumOfMessageWithoutReply)
    print("NumOfMessageWithReply is:", NumOfMessageWithReply)
    print("NumOfTotal is:", NumOfTotal)
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()


def get_sizeof_file(filename, suffix='B'):
    num = os.stat(filename).st_size
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_converted_dic(MessageList):
    MessageListDic = dict()
    NullAccount = 0
    for m in MessageList:
        if len(str(m.AccountNumber))<10:
            NullAccount += 1
        else:
            MessageListDic[m.AccountNumber] = m
    print("Number of WrongMessage is",NullAccount,".")
    return MessageListDic


def get_category(XLSFile, logfile):
    """
    #Build questions buckets
    :param XLSFile:
    :return:List of questions in Excel
    """
    start_time = time.time()

    log = open(logfile, 'a')
    original = sys.stdout

    QuestionList = []
    book = xlrd.open_workbook(XLSFile)
    sh = book.sheet_by_index(4)

    num_rows = sh.nrows - 1
    # num_cells = sh.ncols - 1
    curr_row = 22
    while curr_row < 90:

        print("Row:", curr_row-21,"Class:", sh.cell_value(curr_row, 0))
        curr_row += 1
        QuestionList.append(sh.cell_value(curr_row, 0))
    sys.stdout = Tee(sys.stdout, log)
    print("\nSetting categories from Excel.\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    print("---\tThere are", 90-22, "classes in the Excel.\t---")
    log.close()
    sys.stdout = original
    return QuestionList


def save_object(obj, filename, logfile):
    """
    Save object to file
    :param obj:
    :param filename:
    :return:Success or not
    """
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    with open(filename, 'wb') as output:
        print("\nSaving object to file", filename, "\n---\t",get_time(),"\t---")
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
    print("---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()


def load_object(filename, logfile):
    """
    Load object from file
    :param filename:
    :return:Object saved to file previously
    """
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    with open(filename,'rb') as f:
        print("\nLoading object from file", filename, "\n---\t",get_time(),"\t---")
        pic = pickle.load(f)
        print("---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---")
        print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return pic


def singleAnalysis(Filename,Dic):
    """
    Analyze Single File
    :param Filename: Dic and Dic2 for solve FCR problem
    :return:
    """
    File = open(Dic+Filename,encoding="utf8")
    Text = str(File.readlines())
    File.close()

    message = Message()

    #Check Whether this is a null message


    #Extract Account Number         #1
    a = re.search(r'\d{16}',Text, re.I)
    try:
        message.AccountNumber = Text[a.start():a.end()]
        # print("Account Number is:",message.AccountNumber)
    except:
        message.NullError[1] = True
        return 0

    #Extra Account Name             #2
    n = re.search(r'Name:\s*(.+)\s*\<\s*b\s*r',Text, re.IGNORECASE)
    try:
        message.Name = n.group(1)
        # print("Account Holder's Name is:", message.Name)
    except:
        message.NullError[2] = True

    # Extra Email                   #3
    e =re.search(r'EMail\s*:\s*(.+?)\s*\<\s*b\s*r',Text, re.IGNORECASE)
    try:
        message.Email = e.group(1)
        # print("Account Holder's Email is:", message.Email)
    except:
        message.NullError[3] = True

    # Extra ZIPCODE                 #4
    z =re.search(r'Zip\s*Code\s*:\s*(.+?)\s*\<\s*b\s*r',Text,re.IGNORECASE)
    try:
        message.ZIPCODE = z.group(1)
        # print("Account Holder's Zip Code is:", message.ZIPCODE)
    except:
        message.NullError[4] = True

    #Extra Subject                  #5
    s = re.search(r'Subject\s*:\s*(.*?)\s*\<\s*b\s*r',Text, re.I)
    try:
        s1 = re.sub("RE:","",s.group(1))
        # s1 =  '</b> Re: Re: DirectPay/Automatic Payments [#314051]'
        s1 = re.sub(r'Re:\s*',"",s1)
        s1 = BeautifulSoup(s1).text
        x = re.sub(r'(\[\#\d{6}\])',"",s1)
        x = x.lstrip(" ")
        x = x.rstrip(" ")
        #
        try:
            cID = re.search(r'(\d{6})',s1)
            caseID = cID.group()
            message.CaseID = caseID
        except:
            pass

        # print("modify works")
        message.Subject = x
        message.SubjectFlag = True
        # print("Message's Subject is:", message.Subject)

    except:
        message.NullError[5] = True

    #Extra Content                  #6

    pattern = re.compile(u'<\/?\w+\s*[^>]*?\/?>', re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
    c = pattern.sub(u"", Text)

    try:
        t = "".join(filter(lambda x: x in string.printable, "".join(c)))
        b = BeautifulSoup(t).text
        tt = b.replace('\\n','')
        tt1 = tt.replace('\'','')
        tt2 = tt1.replace(' ,','')
        tt3 = re.sub(r'\s+', ' ',tt2)

        message.Content = tt3
        # print("Message's Content is:", message.Content)
    except:
        message.NullError[6] = True

    message.ReplyTimes = Text.count("Original Message")
    # print("Message's Content is:", message.ReplyTimes)
    Dic2 = get_dic2(Dic)
    # Filename="CC.txt"
    if(message.ReplyTimes>2):
                DirName = Dic2 + "FCR\\"
                if not os.path.exists(os.path.dirname(DirName)):
                    os.makedirs(os.path.dirname(DirName))
                    print("Create file folder", DirName )
                src = Dic2 + Filename
                dst = DirName + Filename
                shutil.copy(src,dst)
    if(message.Subject == ""):
        print("Wrong Subject!!!")
    return message #Return the Message Object


def subjectFinder(srcDic, Dic, logfile):
    """
    Analyze Files in the folder
    :param srcDic:
    :return:
    """
    start_time = time.time()
    # Dic = "MoveTest/"
    # Dic2 = "MoveTest\\"
    # src = srcDic[1]
    ProcessingCounter = 0
    NumOfUnsolved = 0
    NumOfTotal = len(srcDic)
    MessageList = []
    #Percentage = NumOfTotal/100
    #sys.stdout = Tee(sys.stdout, log)
    original = sys.stdout
    log = open(logfile, 'a')
    for filename in srcDic:
        file = filename
        # filename = Dic + FileList[0]
        # filename = src
        # file = Dic + "content957.txt"
        # filename = "content1801.txt"
        # file = "content1801.txt"
        sys.stdout = original
        ProcessingCounter+=1
        print("Checking file", filename, ", which is the",ProcessingCounter,"of", NumOfTotal, "files.")
        sys.stdout = Tee(sys.stdout, log)
        try:
            M = singleAnalysis(file, Dic)
            if (M!=0):
                MessageList.append(M)
            else:
                NumOfUnsolved += 1
            # print("MessageList length:",len(MessageList))
        except:
            NumOfUnsolved += 1
            print("Cannot finish File check for file " + filename+ ", please recheck the file.")


    NumOfMessage = len(MessageList)
    print("\n---\tChecked", NumOfMessage, "messages in total.", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return MessageList


def set_category(QuestionList):
    """
    Set category from Excel Report
    :param QuestionList:
    :return: QsList which is the categories objects list
    """
    QsList = []
    for q in QuestionList:
        Qs = Question()
        Qs.QuestionContent = q
        Qs.QuestionNumber = 0
        QsList.append(Qs)
    HigherCategory = [0,7,11,15,22,26,30,34,44,50,58,61,65]
    for i in HigherCategory:
        QsList[i].Level = 1
    print("\nSetting category done!", "\n---\t",get_time(),"\t---")
    return QsList


def get_otherlist(rawList, QuestionList, logfile):

    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    OtherList = []
    for m in rawList:
        if(get_similarity(str(QuestionList[-2]),str(m.Subject))>0.95):
            OtherList.append(m)
    print("\n---\tFind out", len(OtherList),"\'Other-like\'messages in total.\t---", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return OtherList


def get_FCRlist(rawList, logfile):

    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    FCRList = []
    for m in rawList:
        if(m.ReplyTimes>2):
            FCRList.append(m)
    print("\n---\tFind out", len(FCRList),"\'NON-FCR\'messages in total.\t---", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return FCRList


def get_count_result(QsList, MessageList, logfile):
    start_time = time.time()
    original = sys.stdout

    CountList = []
    ErrorList = []
    for m in MessageList:
        for Qs in QsList:
            if(Qs.Level !=1):
                if(get_similarity(str(Qs.QuestionContent),str(m.Subject))>0.95):
                    Qs.QuestionNumber +=1
                    print("Find subject in--",str(Qs.QuestionContent),"-- with --",str(m.Subject))
                    # print("Matching message and topics .")
                    # print("Matching message and topics . .")
                    # print("Matching message and topics . . .")

                else:
                    ErrorList.append(Qs)
            else:
                Qs.QuestionNumber = 0
    for Qs in QsList:
        CountList.append(Qs)
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    print("\n---\tFind",len(CountList),"messages with corresponding subject.\t---", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return CountList

def output_count_result(QsList):
    for Qs in QsList:
        print("Subject:\t",Qs.QuestionContent,"\t\t\t",Qs.QuestionNumber,"\t")

def output_file(ObjectContent,filename,logfile):
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)

    w = open(filename,'w')
    w.writelines(str(ObjectContent.encode('utf8', 'ignore')))
    w.close()
    print("\n---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()

def output_file_by_message(MessageList, filename, logfile):
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)

    w = open(filename,'w')
    for m in MessageList:
        w.write(str(m.Content.encode('utf8', 'ignore')))
        w.writelines('\n')
    w.close()
    print("\n---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()


def input_file(filename,logfile):
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    sys.stdout = Tee(sys.stdout, log)
    f = open(filename)
    t = f.readlines()
    f.close()
    print("\n---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return t

def join_to_raw_data(InfoList,logfile):
    """

    :param InfoList:
    :return: Joined result of raw data
    """
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')

    RawContent = ""
    for i in range(len(InfoList)):
        RawContent = RawContent+repr(InfoList[i].Content.encode('utf-8'))+'\n'
        print(len(InfoList)-i)
    sys.stdout = Tee(sys.stdout, log)
    print("Joined all content in the list to raw data done.", "\n---\t",get_time(),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return RawContent

def output_to_raw_data(InfoList,filename, logfile):
    """

    :param InfoList:
    :return: Joined result of raw data
    """
    start_time = time.time()
    original = sys.stdout
    log = open(logfile, 'a')
    f = open(filename,'w')
    RawContent = ""
    for i in range(len(InfoList)):
        f.write(InfoList[i].Content)
        print(len(InfoList)-i)
    sys.stdout = Tee(sys.stdout, log)
    print("Joined all content in the list to raw data done.", "\n---\t",get_time(),"\t---")
    print("---\tFile has already been output to file.",filename,"\t---")
    print("---\tSize of the file", filename, "is",get_sizeof_file(filename),"\t---")
    print("---\tTotal", '{:.2f}'.format(time.time()-start_time), "seconds used.\t---")
    sys.stdout = original
    log.close()
    return RawContent


def get_content_fraction(text):
        """
        :param text:
        :return: Content without stopwords and content fraction
        """
        stopwords = nltk.corpus.stopwords.words('english')
        content = [w for w in text if w.lower() not in stopwords]
        print("\nStop word clearance done", "\n---\t",get_time(),"\t---")
        return content,len(content) / len(text)
# ll = load_object(ObjectFile)
# save_object(MessageWithReplyList, ObjectFile1)
# save_object(MessageWithoutReplyList, ObjectFile2)
#

# Dic = "May15_transcripts/"
# Dic2 = "May15_transcripts\\"

# Dic = "May15_transcripts/MessageWithoutReply/"
# Dic2 = "May15_transcripts\\MessageWithoutReply\\"

# Dic = "../MessageWithoutReply/"
# Dic2 = "..\\MessageWithoutReply\\"
#
# Dic = "../MessageWithReply/"
# Dic2 = "..\\MessageWithReply\\"

def main():
    """
    Main Function Control the Whole Work Flow of Analysis
    :return:
    """


    """
    -------------------------------------------------------------------------------
    *******************************************************************************
                            First Stage: Clean Data
    *******************************************************************************
    -------------------------------------------------------------------------------
    """



    """
    -------------------------------------------------------------------------------
    *******************************************************************************
                            Initial Analysis Setting
    *******************************************************************************
    -------------------------------------------------------------------------------
    """
    #Save all works in logfile
    logfile = "Log07121.txt"

    #Default report includes the basic categories for messages
    XLSFile = "eGain Score Card - 2015 (Web).xlsx"

    #Dic1 and Dic2 store the default dictionaries for Message with and without Reply respectively
    Dic1 = "../MessageWithReply/"
    Dic2 = "../MessageWithoutReply/"
    Dic = "MoveTest/"







    """
    -------------------------------------------------------------------------------
    *******************************************************************************
                            Second Stage: Clean Data
    *******************************************************************************
    -------------------------------------------------------------------------------
    """


    #Second Stage
    '''


    '''

    #For messages with reply
    srcDic1 = get_filelist(Dic1, logfile)
    #For messages without reply
    srcDic2 = get_filelist(Dic2, logfile)

    #Test
    # srcDic = get_filelist(Dic, logfile)
    # Message = subjectFinder(srcDic,Dic, logfile)

    #For messages with reply
    Message1 = subjectFinder(srcDic1,Dic1, logfile)
    #For messages without reply
    Message2 = subjectFinder(srcDic2,Dic2, logfile)

    #Save result to file with binary format
    ObjectFile1 = "MessageWithReplyList.pkl"
    ObjectFile2 = "MessageWithoutReplyList.pkl"

    save_object(Message1,ObjectFile1,logfile)
    save_object(Message2,ObjectFile2,logfile)

    #Load binary file from disk

    WithReplyList = load_object(ObjectFile1, logfile)
    WithoutReplyList = load_object(ObjectFile2, logfile)



    #
    #Convernt file to dictionary to speed up
    #

    ddWithReply = get_converted_dic(WithReplyList)
    ddWithoutReply = get_converted_dic(WithoutReplyList)

     #Third Stage
    '''


    '''

    #Dealing with WithReplyList to further analysis
    myList = WithReplyList

    # len(myList)
    #Check the excel and set the category
    QuestionList = get_category(XLSFile, logfile)

    QsList = set_category(QuestionList)


    #Check Subjects in List with Excel Report
    get_count_result(QsList, myList, logfile)

    FileQsList = "QsListFile.pkl"
    save_object(QsList,FileQsList,logfile)
    output_count_result(QsList)


    """
    -------------------------------------------------------------------------------
    *******************************************************************************
                    Analysis of Other-like Subjects Messages
    *******************************************************************************
    -------------------------------------------------------------------------------
    """

    # OtherList = get_otherlist(myList,QuestionList,logfile)

    OtherObjectFile = "OtherObjectFile.pkl"
    # save_object(OtherList,OtherObjectFile,logfile)

    OtherList = load_object(OtherObjectFile,logfile)

    len(OtherList)


    #Join all message to one long string.
    OtherContent = join_to_raw_data(OtherList,logfile)
    len(OtherContent)
    save_object(OtherContent,"OtherContent.pkl",logfile)

    #Output the long string to .txt file
    output_file(OtherContent,"OtherContent.txt",logfile)

    #Directly output the long string to .txt file
    output_file_by_message(OtherList,"OtherListContent.txt", logfile)




    OtherWords = load_object("OtherContent.pkl",logfile)



    Content, fraction = get_content_fraction(OtherWords)
    print("The fraction of non-stop words is",fraction)





    ddOtherList = get_converted_dic(OtherList)
    len(ddOtherList)

    shareOtherdd = set(ddOtherList.keys())&set(ddWithoutReply.keys())
    shareOtherList = list(shareOtherdd)

    [ddWithoutReply[i].Content for i in shareOtherList]

    OnlyQueryContentList = []
    for i in shareOtherList:
        OnlyQueryContentList.append(ddWithoutReply[i])

    len(OnlyQueryContentList)



    output_file_by_message(OnlyQueryContentList,"OnlyQueryOtherListContent.txt", logfile)



    OnlyQueryContent = ""
    for i in shareOtherList:
        OnlyQueryContent = OnlyQueryContent+ddWithoutReply[i].Content+"\n"

    len(OnlyQueryContent)









    """
    -------------------------------------------------------------------------------
    *******************************************************************************
                    Analysis of NON-FCR Messages
    *******************************************************************************
    -------------------------------------------------------------------------------
    """





    # FCRList = get_FCRlist(myList,logfile)

    FCRObjectFile = "FCRObjectFile.pkl"
    # save_object(FCRList,FCRObjectFile,logfile)

    FCRList = load_object(FCRObjectFile,logfile)

    FCRQsList = set_category(QuestionList)

    FCRCountResult = get_count_result(FCRQsList,FCRList,logfile)
    output_count_result(FCRCountResult)



    ddFCRList = get_converted_dic(FCRList)
    len(ddFCRList)

    shareFCRdd = set(ddFCRList.keys())&set(ddWithoutReply.keys())
    len(shareFCRdd)
    shareFCRddList = list(shareFCRdd)
    shareFCRddList[1]
    len(shareFCRddList)
    [ddWithReply[shareFCRddList[i]].Subject for i in range(len(shareFCRddList))]
    AccountMaintenanceList = []
    len(AccountMaintenanceList)

    QuestionListDic = dict()
    QuestionListDic["Account Maintenance"]={"Account Maintenance","Add Person to Account","Cancel Account","Change of Name",
                                            "Other Account Maintenance","Remove Person from Account","Update Contact Information"}

    QuestionListDic["APR"]={"Other Annual Percentage Rate Questions","Promotional Rate Expiration","Request a Lower Annual Percentage Rate"}



    QuestionListDic["Balance Transfer"]={"Balance Transfer Expiration","Other Balance Transfer Questions","Transfer a Balance"}


    QuestionListDic["Billing & Statements"]={"Dispute a Charge","Late Fee - Interest Charges","Other Billing & Statement Questions",
                                         "Question Regarding a Transaction","Statement Request","Pending Transaction"}

    QuestionListDic["Cash Advance"]={"ATM Locations","Other Cash Advance Questions","PIN Number Requests"}

    QuestionListDic["Credit Line"]={"Credit Line Decrease Request","Credit Line Increase Request","Other Credit Line Questions"}

    QuestionListDic["Payments"]={"Credit Balance Refund Request","Due Date","Missing Payment","Online Payments",
                                 "Other Payment Questions","Past Due Arrangements","Payment Cancellations","Payment Options",
                                 "DirectPay - Automatic Payment"}
    QuestionListDic["Replacement Cards"]={"Damaged Cards", "Lost Card Notification","Non-Receipt of a New Card",
                                          "Other Replacement Card Questions","Request a New Design"}

    QuestionListDic["Rewards"]={"5% Quarterly Cashback Bonus Program","Miles","Missing Rewards","Other Rewards Questions",
                                "Redemption Options","ShopDiscover","Discover Deals"}

    QuestionListDic["Travel"]={"Other Travel Questions","Travel Notification"}

    QuestionListDic["Website Help"]={"Error Messages","Mobile Web - App Questions","Navigation in Website"}

    QuestionListDic["Other Questions"]={"Other Questions"}

    QuestionListDic.keys()
    QuestionListDic.items()
    qd = dict()
    for i in QuestionListDic.keys():
        qd[i]=QuestionListDic[]




    for i in range(len(shareFCRddList)):
        # print(ddWithReply[shareFCRddList[i]].Subject)

        if(get_similarity(ddWithReply[shareFCRddList[i]].Subject, "Payments")>0.7):
            print("Find Acc")
            AccountMaintenanceList.append(ddWithoutReply[shareFCRddList[i]])



    print(ddWithoutReply[i] for i in shareFCRddList)
    # sdd1 = sorted(dd1)
    # # sdd1
    # sdd2 = sorted(dd2)
    # # sdd2

    #Count the overlap between message with reply and without reply
    sharedd = set(ddWithReply.keys())&set(ddWithoutReply.keys())
    print("The overlap between messages with reply and without reply is",len(sharedd),".")
    # sharedd = list(sharedd)













    [FCRList[i].Subject for i in range(len(FCRList))]




    [OtherList[i].Subject for i in range(len(OtherList))]
    len(OtherList)





    # xx = str(OtherContent).decode('Windows-1252').encode('utf-8')












#

# [xx[i].Subject for i in range(10)]
# [xx[i].CaseID for i in range(10)]


 #From Report

# Dic = "MoveTest1/"
# Dic = "MoveTest2/"
#
# Dic = "../MoveTest/"
# srcDic = get_filelist(Dic, logfile)
# mm = subjectFinder(srcDic, Dic,logfile)





# len(WithoutReplyList)
#
#
# dd1 = get_converted_dic(Message1)
# dd2 = get_converted_dic(Message2)
#
# len(WithReplyList)
# len(dd1.keys())
# len(WithoutReplyList)
# len(dd2.keys())









# Qs = Question()

#

# len(myList)


#
# # def QuestionSum(QsList):
# #     QsList[0].QuestionNumber = sum(QsList[1,2,3,4,5].QuestionNumber)
#


[QsList[i].Level for i in range(30)]
#QuestionList store all questions in the Excel (string list)
#QsList store all question objects in the Excel (with count)



# len(MessageList)
get_count_result(QsList, WithReplyList[:500], logfile)




import numpy as np

HigherCategory = [0,7,11,15,22,26,30,34,44,50,58,61,65]
np.cumsum(QsList[HigherCategory].QuestionNumber)

    # for q in QsList:
    #     if(q.Level == 1):
    #         q.QuestionNumber +=


i = 0
sum(QsList[i+1:HigherCategory[i+1]].QuestionNumber)





len(OtherList)

[OtherList[i].Subject for i in range(1000)]

[FCRList[i].Subject for i in range(1000)]



# ErroorList = []
#
# # len(ErrorList)
#
# QuestionList[-2]



#
#
# for Qs in QsList:
#     print(Qs.QuestionContent,":  ",Qs.QuestionNumber,"--")
#
# for m in myList[:100]:
#     print(m.Subject)

# To analyze single text file
# Dic = "MoveTest/"
# Dic2 = "MoveTest\\"
# Filename = "CC.txt"
# m = singleAnalysis(Filename)



# MessageList = []




if __name__ == "__main__":
    main()
