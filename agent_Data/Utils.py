'''
Created on 20 Jul 2017

@author: zhi liang
'''
from itertools import groupby
import re
import csv
import codecs
from datetime import datetime as dt


OUTPUT_PATH = 'C:\\Users\\Admin\\workspace\\python.first\\src\\agent_Data\\OUTPUT_CASE_DATA'
mapTransitionsToStates = {'OTP Issued':'WIP(2)', 'Excl. Ext.':'WIP(1)',
                          'Lost ( Oth. Agent )':'Lost', 'Excl. Ter. ( Client )':'Lost',
                          'Lost ( Spec. )':'Lost', 'Excl. Ter. ( OMH )':'Lost', 
                          'In Progress':'WIP(1)'}
mapTransitionsToAdd = {'OTP Issued':'monthClosed', 'Excl. Ext.':'monthExtended', 'In Progress': 'monthReopened',
                      'Lost ( Oth. Agent )':'monthLostByOthers', 'Excl. Ter. ( Client )':'monthLostByClient',
                      'Lost ( Spec. )':'monthLostBySpec', 'Excl. Ter. ( OMH )':'monthLostByOMH', 'Reopened':'monthReopened'}

def removeBlanks(transactionData):
    transactionData = [x for x in transactionData if not x['Case ID']]
    return transactionData

def getTransitions(case, WIP1, errorList):
    
    transitions = [(case['Result 1'], case['Rep. Date 1']), 
                   (case['Result 2'], case['Rep. Date 2']), 
                   (case['Result 3'], case['Rep. Date 3']),
                   (case['Result 4'], case['Rep. Date 4']), 
                   (case['Result 5'], case['Rep. Date 5']),
                   (case['Result 6'], case['Rep. Date 6']),
                   (case['Result 7'], case['Rep. Date 7']),
                   (case['Result 8'], case['Rep. Date 8'])]
    transitions = [x[0] for x in groupby(transitions)]
  
    dates = [dt.strptime(case['Rec. Date'], '%d-%b-%y'), dt.strptime(case['Advert. Date'], '%d-%b-%y')]
    
    for transition in transitions:
        
        if (transition[0] == 'In Progress' and len(transition[1]) == 0):
            continue
        else:
            dates.append(dt.strptime(transition[1], '%d-%b-%y'))
            
        
    if (not checkForValidity(dates)):
        errorList.append(case['Case ID'])
        print('case ID ' + str(case['Case ID']) + ' has an error! PLEASE RECTIFY NOOB')

    transitions = [x[0] for x in groupby(transitions)]

    if (len(transitions) == 1):
        transitions = list(filter(lambda a: a[0] != 'In Progress', transitions))
    transitions = [(mapTransitionsToAdd[transition[0]],transition[1]) for transition in transitions]
    return transitions

def getLastState(case):
    lastTransition = case['Result 8']
    return mapTransitionsToStates[lastTransition]

def update(json1_data_total, transitions, case, caseTracker):
    for transition in transitions:
        transitionEvent = transition[0]

        indices = [s.start() for s in re.finditer('-', transition[1])]
        transitionMonth = transition[1][indices[0]+1:]
        json1_data_total[transitionEvent][transitionMonth] += 1
        if (transitionEvent == 'WIP(1)'):
            caseTracker[transitionEvent][transitionMonth].append((case['Case ID'], case['Rec. Date']))
        elif (transitionEvent == 'WIP(2)'):
            caseTracker[transitionEvent][transitionMonth].append((case['Case ID'], case['Rec. Date'], transition[1]))
        else:
            caseTracker[transitionEvent][transitionMonth].append((case['Case ID'], case['Rec. Date'], transition[1]))


def collateID(listReopened, monthReopened):
    for month in monthReopened:
        for case in monthReopened[month]:
            listReopened.append(case[0])

def collateLost(lostByMonth, caseTracker):
    months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
              'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
    for month in months:
        listToAdd = []
        listToAdd.extend(caseTracker['monthLostByOMH'][month])
        listToAdd.extend(caseTracker['monthLostByClient'][month])
        listToAdd.extend(caseTracker['monthLostByOthers'][month])
        listToAdd.extend(caseTracker['monthLostBySpec'][month])
        lostByMonth[month] = listToAdd
            
def checkForValidity(dates):
    for x in range(len(dates) - 1):
        if (dates[x] > dates[x+1]):
            return False
    return True  

def isValid(events, errorList, caseID):
    lostPhrase = ['Lost ( Oth. Agent )', 'Excl. Ter. ( Client )',
                  'Lost ( Spec. )', 'Excl. Ter. ( OMH )']
    lost = [x for x in events if x in lostPhrase]
    if (len(lost) > 0):
        lost = list(set(lost))
        if (len(lost) > 0): #check if only one kind of lost
            errorList.append(caseID)
            return
        if (events.index(lost[0]) != (len(events) - 1)): #check if lost is last event
            errorList.append(caseID)
            return
    if ('OTP Issued' in events and 'Excl. Ext.' in events and 'Reopened' not in events):
        if (events.index('OTP Issued') < events.index('Excl. Ext.')):
            errorList.append(caseID)
            return
    
    
def removeDuplicates(lst):
    containedIDs = []
    lstRemoveDuplicates = []
    for x in reversed(lst):
        if (x not in containedIDs):
            lstRemoveDuplicates.append(x)
            containedIDs.append(x)
    lst = lstRemoveDuplicates 
    return lst
      
        

def writeToCSV_currentWIP1(WIP1):
    with codecs.open(os.path.join(OUTPUT_PATH, 'WIP(1)_atTheMoment.csv'), 'w', 'utf-8') as file:
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Case ID', 'Agent', 'First Recorded Date', 'Week'])
        for cases in WIP1:
            inputline = [cases[0],cases[1],cases[2],cases[3]]
            filewriter.writerow(inputline)
        file.close()
def writeToCSV_currentWIP2(WIP2):
    with codecs.open(os.path.join(OUTPUT_PATH,'WIP(2)_atTheMoment.csv'), 'w', 'utf-8') as file:
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Case ID', 'Agent', 'First Recorded Date', 'Closed Date'])
        for cases in WIP2:
            inputline = [cases[0],cases[1],cases[2],cases[3]]
            filewriter.writerow(inputline)
        file.close()
def writeToCSV_currentLost(Lost):
    with codecs.open(os.path.join(OUTPUT_PATH,'Lost_Cases.csv'), 'w', 'utf-8') as file: 
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Case ID', 'Agent', 'First Recorded Date', 'Lost'])
        for cases in Lost:
            inputline = [cases[0],cases[1],cases[2],cases[3]]
            filewriter.writerow(inputline)

        file.close()
def writeToCSV_newCase_byMonth(caseTracker):
    with codecs.open(os.path.join(OUTPUT_PATH,'cases_newCase_byMonth.csv'), 'w', 'utf-8') as file: 
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
       
        months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
                  'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
        row1 = []
        row2 = []
        for month in months:
            row1.extend([month, ' '])
            row2.extend(['Case ID', 'Rec. Date'])
        filewriter.writerow(row1)
        filewriter.writerow(row2)
    
        toWrite = []
        for month in months:
            toWrite.append(caseTracker['monthNew'][month])
        maxListingPerMonth = max([len(x) for x in toWrite])
        for count in range(maxListingPerMonth):
            listToWrite = []
            for x in range(len(months)):
                try:
                    case = list(toWrite[x][count])
                    listToWrite.extend(case)
                except:
                    listToWrite.append(' ')
                    listToWrite.append(' ')
            filewriter.writerow(listToWrite)
        file.close()       
def writeToCSV_lostCase_byOMH_byMonth(caseTracker):
    with codecs.open(os.path.join(OUTPUT_PATH,'cases_lostCase_byOMH_byMonth.csv'), 'w', 'utf-8') as file: 
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        
        months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
                  'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
        
        row1 = []
        row2 = []
        for month in months:
            row1.extend([month, ' ', ' '])
            row2.extend(['Case ID', 'Rec. Date', 'Lost Date'])
        filewriter.writerow(row1)
        filewriter.writerow(row2)
        
        toWrite = []
        for month in months:
            toWrite.append(caseTracker['monthLostByOMH'][month])
        maxListingPerMonth = max([len(x) for x in toWrite])
        for count in range(maxListingPerMonth):
            listToWrite = []
            for x in range(len(months)):
                try:
                    case = list(toWrite[x][count])
                    listToWrite.extend(case)
                except:
                    listToWrite.append(' ')
                    listToWrite.append(' ')
                    listToWrite.append(' ')
            filewriter.writerow(listToWrite)
        file.close()
def writeToCSV_lostCase_byClient_byMonth(caseTracker):
    with codecs.open(os.path.join(OUTPUT_PATH,'cases_lostCase_byClient_byMonth.csv'), 'w', 'utf-8') as file: 
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        
        months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
                  'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
        
        row1 = []
        row2 = []
        for month in months:
            row1.extend([month, ' ', ' '])
            row2.extend(['Case ID', 'Rec. Date', 'Lost Date'])
        filewriter.writerow(row1)
        filewriter.writerow(row2)
        
        toWrite = []
        for month in months:
            toWrite.append(caseTracker['monthLostByClient'][month])
        maxListingPerMonth = max([len(x) for x in toWrite])
        for count in range(maxListingPerMonth):
            listToWrite = []
            for x in range(len(months)):
                try:
                    case = list(toWrite[x][count])
                    listToWrite.extend(case)
                except:
                    listToWrite.append(' ')
                    listToWrite.append(' ')
                    listToWrite.append(' ')
            filewriter.writerow(listToWrite)
        file.close()
def writeToCSV_lostCase_byOtherAgents_byMonth(caseTracker):
    with codecs.open(os.path.join('C:\\Users\\Admin\workspace\\python.first\\src\\agent_Data\\OUTPUT_CASE_DATA','cases_lostCase_byOtherAgents_byMonth.csv'), 'w', 'utf-8') as file: 
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        
        months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
                  'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
        
        row1 = []
        row2 = []
        for month in months:
            row1.extend([month, ' ', ' '])
            row2.extend(['Case ID', 'Rec. Date', 'Lost Date'])
        filewriter.writerow(row1)
        filewriter.writerow(row2)
        
        toWrite = []
        for month in months:
            toWrite.append(caseTracker['monthLostByOthers'][month])
        maxListingPerMonth = max([len(x) for x in toWrite])
        for count in range(maxListingPerMonth):
            listToWrite = []
            for x in range(len(months)):
                try:
                    case = list(toWrite[x][count])
                    listToWrite.extend(case)
                except:
                    listToWrite.append(' ')
                    listToWrite.append(' ')
                    listToWrite.append(' ')
            filewriter.writerow(listToWrite)
        file.close()
def writeToCSV_lostCase_bySpecial_byMonth(caseTracker):
    with codecs.open(os.path.join(OUTPUT_PATH,'cases_lostCase_bySpecialReasons_byMonth.csv'), 'w', 'utf-8') as file: 
        filewriter = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)

        months = ['May-16', 'Jun-16', 'Jul-16', 'Aug-16', 'Sep-16', 'Oct-16', 'Nov-16', 'Dec-16', 'Jan-17', 'Feb-17',
                   'Mar-17', 'Apr-17', 'May-17', 'Jun-17', 'Jul-17', 'Aug-17', 'Sep-17', 'Oct-17', 'Nov-17', 'Dec-17']
        row1 = []
        row2 = []
        for month in months:
            row1.extend([month, ' ', ' '])
            row2.extend(['Case ID', 'Rec. Date', 'Lost Date'])
        filewriter.writerow(row1)
        filewriter.writerow(row2)
        toWrite = []
        for month in months:
            toWrite.append(caseTracker['monthLostBySpec'][month])
        maxListingPerMonth = max([len(x) for x in toWrite])
        for count in range(maxListingPerMonth):
            listToWrite = []
            for x in range(len(months)):
                try:
                    case = list(toWrite[x][count])
                    listToWrite.extend(case)
                except:
                    listToWrite.append(' ')
                    listToWrite.append(' ')
                    listToWrite.append(' ')
            filewriter.writerow(listToWrite)
        file.close()
import os

import xlwt # from http://www.python-excel.org/
count = 0
wb = xlwt.Workbook()
sheetName = ['byClient', 'byOMH', 'byOtherAgents', 'Special']
for csvfile in os.listdir(OUTPUT_PATH + '\\'):
    if (not csvfile.startswith('cases_lostCase_by')):
        continue
    ws = wb.add_sheet(sheetName[count])
    with open(OUTPUT_PATH + '\\' + csvfile, 'r', encoding = 'utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, val in enumerate(row):
                if (isinstance(val,int)):
                    val = str(val)
                    while (len(val)<6):
                        val = '0' + val
                if (r <= 2):
                    ws.write(r, c, val)
                else:
                    ws.write(r, c, val)
    wb.save('combined_lostCases_byMonth.xls')   
    count = count + 1
