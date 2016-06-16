# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 16:03:42 2016

@author: Michael
"""

def find(needles, haystack):
    haystack_length = len(haystack)
    val = 0
    for needle in needles:
        new_haystack_length = len(haystack.replace(needle,''))
        if haystack_length != new_haystack_length:
            val=1
    return(val)

#file = 'G:/2016 Projects/621- Voter Participation in Monroe County/Data/participation.txt'

file = 'G:/2016 Projects/621- Voter Participation in Monroe County/Mapping/R/ActiveVoters.csv'
i=0
the_2012_elections = ['12 GENERAL  ELECTION', '2012 GENERAL ELECTION','2012 General Election','2012 PRES  ELECTION','2012 STATE AND LOCAL GENERAL ELECT','20121106 GE', 'GENERAL 2012', 'GENERAL ELECTION 2012', 'General Election 2012']
the_2013_elections = ['13 PRIMARY ELECTION', '2013 Primary Election', '2013 PRIMARY ELECTION', '2013 SEPTEMBER PRIMARY ELECTION', '20130910 PR', 'PR 20130910', 'PRIMARY 2013', 'PRIMARY ELECTION 2013', 'Primary Election 2013']
the_2014_elections = ['14 GENERAL  ELECTION', '2014  GENERAL ELECTION', '2014 GENERAL ELECTION', '2014 General Election', '20141104 GE', 'GENERAL 2014', 'GENERAL ELECTION 2014', 'General Election 2014', 'GENERAL STATE & LOCAL ELECTION 2014']
the_2015_elections = ['15 GENERAL ELECTION', '2015  GENERAL ELECTION', '2015 GENERAL ELECTION', '2015 General Election', '20151103 GE','GENERAL 2015','GENERAL ELECTION 2015','General Election 2015']
elections = list()
counts = dict()
votes = list()
for line in open(file, 'r', encoding='latin-1'):
    i = i+1
    print('Row: '+str(i))
    pos = line.find('"NY0000')
    if pos == -1: continue
    
    items = line[pos:].strip().split(',')
    voter_id = items[0].strip('"')
    
    voter_history = items[1].strip('"')
    voted_in_2012 = find(the_2012_elections, voter_history)
    voted_in_2013 = find(the_2013_elections, voter_history)
    voted_in_2014 = find(the_2014_elections, voter_history)
    voted_in_2015 = find(the_2015_elections, voter_history)
    voter_history = voter_history.split(';')
    #print(str(len(voter_history)))
    
    votes.append((voter_id, voted_in_2012, voted_in_2013, voted_in_2014, voted_in_2015, len(voter_history)))
    
    for item in voter_history:
        counts[item] = counts.get(item,0)+1
        if item not in elections:
            elections.append(item)

import pandas as pd
#df = pd.DataFrame(elections, columns=["colummn"])
#df.to_csv('list.csv', index=False)

df = pd.DataFrame(votes, columns=['SBOEID','voted_in_2012','voted_in_2013','voted_in_2014','voted_in_2015','times_voted'])
df.to_csv('votes.csv', index=False)