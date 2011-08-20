#!/usr/bin/env python3
 
#####
# Hard Constraints:
# - Es gibt zwei Wegpunkte: Oldenburg und Varel
# - Wer hin fährt, muss auch zurück kommen
# - In einem Auto sitzen 4 oder weniger Personen
# - wenn nur eine Person im Auto ist, muss es ihres sein
# - Jeder hat ein Auto
# - Gefahren wird Montags bis einschl. Freitags
# - Jeden Tag gibts Schulstunden von 1 bis 9
# - Kein Warten nach dem Ende des Tages
# - Kein zu früh zur Arbeit fahren
# - Wenn ein Auto hinfährt, muss es auch wieder zurück
#
# Soft Constraints:
# - Niemand sollte häufiger als 3 mal die Woche fahren
# - Weniger Wartezeiten sind besser
# - Dieselben Besetzungen ?

# Eingabe:
# FOR person in Personen:
#   FOR tag in Tagen:
#      anfahrt = Stundenzahl
#      abfahrt = stundenzahl

import csv,pprint
from random import choice

# read data
reader = csv.reader(open("data.csv"))
# throw away headings
next(reader)
# read data and construct data structure
days = ["mo","di","mi","do","fr"]
datastore = {}
for day in days:
    hours = dict.fromkeys(range(1,10))
    for hour in hours:
        hours[hour] = {'hin': [], 'rück': []}
    datastore[day] = hours

# now fill in the data
for row in reader:
    name = row[0]
    for i in range(1,11):
        direction = "hin" if i%2 else "rück"
        hour = int(row[i])
        datastore[days[int((i-1)/2)]][hour][direction].append(name)
    
def create_groups(ori_people):
    people = list(ori_people)
    if not people:
        return []
    amount = len(people)
    amount_groups = amount//4 if amount%4==0 else (amount//4)+1
    groupsize=amount//amount_groups
    groups=[]
    for i in range(0,amount_groups):
        group = {"driver": None, "people":[]}
        for i in range(0,groupsize):
            person = choice(people)
            people.remove(person)
            group['people'].append(person)
        groups.append(group)
    return groups         

plan = datastore.copy()
# now we gotta decide who drives with whom
for day, data in datastore.items():
    # make room to note drivers
    loners=set()
    for hour in data.keys():
        plan[day][hour]['hin'] = {'people':plan[day][hour]['hin'],"drivers":[]}
        plan[day][hour]['rück'] = {'people':plan[day][hour]['rück'],"drivers":[]}
        plan[day][hour]['cars'] = 0
        # whoever has to drive alone at some point becomes a driver
        if len(plan[day][hour]['hin']['people'])==1:
            loners.add(plan[day][hour]['hin']['people'][0])
        if len(plan[day][hour]['rück']['people'])==1:
            loners.add(plan[day][hour]['rück']['people'][0])
    # now we marked to people who have to drive alone in one direction, 
    # let's make them drivers for their other way as well
    for hour in data.keys():
        for person in plan[day][hour]['hin']['people']:
            if person in loners:
                plan[day][hour]['hin']['drivers'].append(person)

        for person in plan[day][hour]['rück']['people']:
            if person in loners:
                plan[day][hour]['rück']['drivers'].append(person)



    

pprint.pprint(plan)
