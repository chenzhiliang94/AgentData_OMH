'''
Created on 20 Jul 2017

@author: zhi liang
'''
import unicodecsv
import json
import os
from src.agent_Data.Utils import getTransitions, getLastState,\
    update, writeToCSV_currentWIP1, writeToCSV_currentWIP2,\
    writeToCSV_currentLost, writeToCSV_newCase_byMonth,\
    writeToCSV_lostCase_byOMH_byMonth, writeToCSV_lostCase_byClient_byMonth,\
    writeToCSV_lostCase_byOtherAgents_byMonth,\
    writeToCSV_lostCase_bySpecial_byMonth, collateID, collateLost,\
    removeDuplicates
import re
import codecs
import csv
from datetime import datetime as dt
import time
import math

def file_reader(filename):
    with open(filename,'rb') as f:
        reader = unicodecsv.DictReader(f)
        contents = list(reader)
    return contents

transactionData = file_reader("Data Sample_CSV.csv")
transactionData = [x for x in transactionData if (not x['Case ID'] == '')]
for items in transactionData:
    caseID = str(items['Case ID'])
    while (len(caseID)<6):
        caseID = '0' + caseID
    items['Case ID'] = caseID
    
json1_file_total = open("overview.txt")
json1_str = json1_file_total.read()
json1_data_total = json.loads(json1_str)

json1_file_total = open("overviewWithCaseID.txt")
json1_str = json1_file_total.read()
caseTracker = json.loads(json1_str)

WIP1 = []
WIP2 = []
lost = []
states = {'WIP(1)':WIP1, 'WIP(2)':WIP2, 'Lost': lost}
errorList = []

for case in transactionData:
    try:
        caseID = case["Case ID"]
        recDate = case['Rec. Date'] #first signed date for this new case
        indices = [s.start() for s in re.finditer('-', recDate)]
        month = recDate[indices[0]+1:]
        json1_data_total['monthNew'][month] += 1
        caseTracker['monthNew'][month].append((case['Case ID'], case['Rec. Date']))
        transitions = getTransitions(case, states['WIP(1)'], errorList)
        if (len(errorList) > 0):
            continue
        update(json1_data_total, transitions, case, caseTracker)
        if (getLastState(case) == 'WIP(1)'):
            startDate = case['Rec. Date']
            datetime_object_start = dt.strptime(startDate, '%d-%b-%y').date()
            datetime_object_now = dt.strptime((time.strftime("%Y-%m-%d")), '%Y-%m-%d').date()
            caseDuration = (datetime_object_now - datetime_object_start).days
            assert (caseDuration >= 0), "error at case ID " + case['Case ID'] + ": recorded date later than current date"      
            weeksInProgress = math.ceil(caseDuration/7)
            states[getLastState(case)].append((case['Case ID'], case['Agent'], case['Rec. Date'], weeksInProgress))
        else:
            states[getLastState(case)].append((case['Case ID'], case['Agent'], case['Rec. Date'], case['Rep. Date 8']))
    except:
        errorList.append(case['Case ID'])
        continue


#print(caseTracker)
#print(json1_data_total)
OUTPUT_PATH = 'C:\\Users\\Admin\\workspace\\python.first\\src\\agent_Data\\OUTPUT_CASE_DATA'
with open(os.path.join(OUTPUT_PATH,'overviewCasesAmount.txt'), "w") as file1:
    file1.write(str(json1_data_total))
    
with open(os.path.join(OUTPUT_PATH,'overviewCasesID.txt'), "w") as file1:
    file1.write(str(caseTracker))
    
if (len(errorList) > 0):
    print('THERES ERROR IN FILE! DISPLAYING ALL ERRORS:')
    for error in errorList:
        print(error)
    quit()


writeToCSV_newCase_byMonth(caseTracker)
writeToCSV_currentWIP1(states['WIP(1)'])
writeToCSV_currentWIP2(states['WIP(2)'])
writeToCSV_currentLost(states['Lost'])
writeToCSV_lostCase_byOMH_byMonth(caseTracker)
writeToCSV_lostCase_byClient_byMonth(caseTracker)
writeToCSV_lostCase_byOtherAgents_byMonth(caseTracker)
writeToCSV_lostCase_bySpecial_byMonth(caseTracker)


with codecs.open(os.path.join(OUTPUT_PATH,'overall.csv'), 'w', 'utf-8') as file: 
    filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['Month', 'In Progress',' ', 'In Progress',' ', 'OTP Issued',' ', 'OTP Issued',' ', 'Lost', 'Lost']) 
    filewriter.writerow([' ', 'Monthly - Total', 'Cumulative - Total', 'Monthly - Reopened', 'Cumulative - Reopened', 'Monthly - Total', 'Cumulative - Total', 'Monthly - Excluding Reopened', 'Cumulative - Excluding Reopened', 'Monthly', 'Cumulative'])
    listReopened = []
    collateID(listReopened, caseTracker['monthReopened'])
    lostByMonth = {}
    collateLost(lostByMonth, caseTracker)
    #reopenedClosedIDByMonth = {}
    cumulativeClosedIDByMonth = {}
    inProgressList = []
    closedList = []
    reopenedList = []
    inProgressReopened = {} #cases with these status but are reopened ones
    ClosedReopened = {}
    LostReopened = {}
    reopenedCasesTemp = caseTracker['monthReopened']['May-16']
    months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
              'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
    month = 'May-16'
    cumulativeInProgress = [x for x in caseTracker['monthNew']['May-16'] if (x not in lostByMonth['May-16'] and x not in caseTracker['monthClosed']['May-16'])]
    cumulativeLost = lostByMonth['May-16']
    cumulativeClosed = caseTracker['monthClosed']['May-16']
    temp = cumulativeClosed 
    cumulativeClosedIDByMonth['May-16'] = temp
    inProgressMonth = {}
    inProgressMonth['May-16'] = len(cumulativeInProgress)
    reopenedBefore = []
    reopenedIP = 0
    reopenedClosed = 0
    reopenedLost = 0
    #cumulativeClosedIDByMonth['May-16'] = [x[0] for x in cumulativeClosed]
    toWrite = [month, len(caseTracker['monthNew'][month] + caseTracker['monthReopened'][month]), len(cumulativeInProgress),
                   len(caseTracker['monthReopened'][month]), reopenedIP, len(caseTracker['monthClosed'][month]), len(cumulativeClosed),
                   (len(caseTracker['monthClosed'][month])), len(cumulativeClosed) - reopenedClosed, len(lostByMonth[month]),
                   len(cumulativeLost)]
    filewriter.writerow(toWrite)
    for month in months:
        toWrite.append(month)
        if (month == 'May-16'):
            continue
        incomingNewCase = caseTracker['monthNew'][month]
        outgoingLostCase = lostByMonth[month]
        
        closedCases = [x for x in caseTracker['monthClosed'][month] if x[0] not in [y[0] for y in outgoingLostCase]]
        reopenedCases = [x for x in caseTracker['monthReopened'][month] if x[0] not in [y[0] for y in outgoingLostCase]]
        reopenedCasesTemp.extend(caseTracker['monthReopened'][month])
        incomingNewCase = [x for x in incomingNewCase if (x[0] not in [y[0] for y in closedCases])]
        cumulativeInProgress.extend(incomingNewCase)
        cumulativeInProgress = [x for x in cumulativeInProgress if x[0] not in [y[0] for y in outgoingLostCase]]
        cumulativeClosed = [x for x in cumulativeClosed if x[0] not in [y[0] for y in outgoingLostCase]]
        cumulativeLost.extend(outgoingLostCase)
        if (reopenedCases):
            reopenedBefore.extend([x[0] for x in reopenedCases])
            reopenedCasesDone = []
            for case in reopenedCases:
                if case[0] in [x[0] for x in reopenedCasesDone]:
                    continue 
                if case[0] not in [x[0] for x in closedCases]:
                    continue
                reopenedID = case[0]
                reopenedCaseListofID = [x for x in reopenedCases if (x[0] == reopenedID)]
                lastReopenedDate = reopenedCaseListofID[-1][2]
                temp = [x for x in closedCases if (x[0] == reopenedID)]
                lastClosedDate = temp[-1][2]
                lastReopenedDate = dt.strptime(lastReopenedDate, '%d-%b-%y')
                lastClosedDate = dt.strptime(lastClosedDate, '%d-%b-%y')
                if (lastReopenedDate > lastClosedDate):
                    closedCases = [x for x in closedCases if (not x[0] == reopenedID)]
                else:
                    reopenedCasesDone.append(case)
            reopenedCases = [x for x in reopenedCases if (not x in reopenedCasesDone)]
        
        cumulativeClosed.extend(closedCases)
        cumulativeClosed = [x for x in cumulativeClosed if (x[0] not in [y[0] for y in reopenedCases])]
        containedClosed = []
        cumulativeClosedRemoveDuplicates = []
        for x in reversed(cumulativeClosed):
            if (x[0] not in containedClosed):
                cumulativeClosedRemoveDuplicates.append(x)
                containedClosed.append(x[0])
        cumulativeClosed = cumulativeClosedRemoveDuplicates
        cumulativeInProgress.extend(reopenedCases)
        containedInProgress = []
        cumulativeInProgressRemoveDuplicates = []
        for x in reversed(cumulativeInProgress):
            if (x[0] not in containedInProgress):
                cumulativeInProgressRemoveDuplicates.append(x)
                containedInProgress.append(x[0])
        cumulativeInProgress = cumulativeInProgressRemoveDuplicates
        cumulativeInProgress = [x for x in cumulativeInProgress if x[0] not in [y[0] for y in cumulativeClosed]]
        reopenedIP = len(removeDuplicates([w for w in reopenedBefore if w in [y[0] for y in cumulativeInProgress]]))
        reopenedClosed = len(removeDuplicates([w for w in reopenedBefore if w in [y[0] for y in cumulativeClosed]]))
        reopenedLost = len([w for w in reopenedBefore if w in [y[0] for y in cumulativeLost]]) 
        toWrite = [month, len(caseTracker['monthNew'][month] + caseTracker['monthReopened'][month]), len(cumulativeInProgress),
                   len(caseTracker['monthReopened'][month]), reopenedIP, len(caseTracker['monthClosed'][month]), len(cumulativeClosed),
                   (len([x for x in caseTracker['monthClosed'][month] if (x[0] not in [y[0] for y in reopenedCasesTemp])])), len(cumulativeClosed) - reopenedClosed, len(lostByMonth[month]),
                   len(cumulativeLost)]
        filewriter.writerow(toWrite)
     
        cumulativeClosedIDByMonth[month] = cumulativeClosed
        


currentCumulativeClosed = cumulativeClosed

with codecs.open(os.path.join(OUTPUT_PATH,'OTP_Issued_Fluctuating.csv'), 'w', 'utf-8') as file: 
    filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    for month in months:
        toWrite = [month]
        info = [x[0] for x in cumulativeClosedIDByMonth[month] if (x in currentCumulativeClosed)]
        toWrite.append(len(info))
        filewriter.writerow(toWrite)


