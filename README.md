
*Created by Zhi Liang 1/8/2017*

Default files in folder:

- **main.py** - Main python file to read the input

- **Utils.py** - Contains functions to process the data and calculate how many transitions happened in each month (e.g Lost, OTP Issued)

- **overview.txt** - Contains the python dictionary structure for how many cases of each type for each month (e.g Lost, OTP Issued etc)

- **overviewWithCaseID.txt** - Similar to overview.txt, but contains the specific Case ID instead of merely total number of cases for each type

-- Output files which will be written to OUTPUT_CASE_DATA:
- cases_lostCase_byClient_byMonth.csv - How many lost cases (Terminated by clients) per month (by ID)
- cases_lostCase_byOMH_byMonth.csv - How many lost cases (Terminated by clients) per month (by ID)
- cases_lostCase_byOtherAgents_byMonth.csv - How many lost cases (Terminated by clients) per month (by ID)
- cases_lostCase_bySpecialReasons_byMonth.csv - How many lost cases (Terminated by clients) per month (by ID)
- cases_newCase_byMonth.csv - How many new cases per month (by ID)
- Lost_Cases.csv - Total lost cases currently (by ID)
- OTP_Issued_Fluctuating.csv - How many OTP Issued cases for each month which are not lost or reopened currently (Retrospect view)
- overall.csv - MOST IMPORTANT CSV WHICH SUMMARISES EVERYTHING
- overviewCasesAmount.txt - Same dictionary as overview.txt, but now with the values filled in
- overviewCasesID.txt - Same dictionary as overviewWithCaseID.txt, but now with the values filled in
- WIP(1)_atTheMoment.csv - Number of cases which are In Progress at the current moment (by ID)
- WIP(2)_atTheMoment.csv - Number of cases which are OTP Issued at the current moment (by ID)

***

***Methodology1*** - Collating new cases, lost cases, last states and all transitions per month (Easy)
line 51-102
1. Scan through each case and identify the first recorded date, transitions and transition dates that occured for each case (Possibly up to 8 transitions)
(See function: getTransitions(case, WIP1, errorList) )
2. Errors are identified by looking at the dates order of each transition (Must be ascending order) and the order of transition.
(Identify illogical transition orders: e.g Lost case -> OTP Issued not possible!)
3. Transitions can be classified as:
- monthNew
- monthLostByOMH
- monthLostByClient
- monthLostByOthers
- monthLostBySpec
- monthClosed
- monthExtended
- monthReopened
4. To identify the In Progress cases, OTP Issued cases and lost cases currently, we simply identify the last transition for each case (see function: getLastState(case) )
5. Results are written into the relevant CSV file and into the text

***

***Methodology2*** - Collating cumulated OTP Issued Cases, cumulated In Progress Cases (Hard)
line 104-205
1. Look at the number of new cases, lost cases, reopened cases, OTP Issued cases every month by ID to identify how many cases are at what states at the end of each month.
2. For example, if case 000001 and 000002 are new cases in May, then end of the month there are 2 cumulative In Progress cases. In June, let’s say we have 2 more new cases: 000003 and 000004. But also in June, case 000001 is OTP Issued, case 000002 is Lost and case 000003 is OTP Issued in the same month. Then at the end of June, we have case 000004 as cumulative In Progress, 000001 and 000003 are cumulative OTP Issued, and 000002 is cumulative Lost.
Since we have case ID for each type of transition for each month previously in methodology1 and the date of each transition, we are able to identify where each case ID is at the end of each month and count the cumulated amount for each type of states.
3. In the scenario of one case going through multiple transitions in one month (The most probable being OTP Issued – Reopened – OTP Issued), we identify the latest date transition for that case in that month and tag that case ID to that particular transition. This is where the case is at the end of the month.

***

***Methodology3*** - Collating OTP Issued Cases in retrospect (How many closed cases in a month which isn’t lost afterwards)
line 210-216
1. Methodology1 allows us to have the lost cases ID currently. Methodology2 allows us to have the cumulative OTP Issued cases ID for each month and cumulative In Progress Cases ID for each month. For the last part, we simply do a cross check so that we remove reopened cases and lost cases from the cumulative OTP Issued cases per month and obtain a retrospect cumulative amount of OTP Issued cases per month which are not lost or reopened currently.
