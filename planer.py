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
from random import choice,shuffle

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
        hours[hour] = {'hin': [], 'rück': [], }
    datastore[day] = hours

# now fill in the data
for row in reader:
    name = row[0]
    for i in range(1,11):
        direction = "hin" if i%2 else "rück"
        try:
            hour = int(row[i])
            if hour!=-1:
                datastore[days[int((i-1)/2)]][hour][direction].append(name)
        except:
            pass
    
def assign(plan,day,hour,direction):
    people = list(plan[day][hour][direction]["people"])
    drivers = list(plan[day][hour][direction]["drivers"])
    groups=[]
    if not people:
        return []
    for person in drivers:
        groups.append({'driver':person,'people':[]})
        people.remove(person)
    if not people:
        return groups
    amount = len(people)
    amount_groups = amount//4 if amount%4==0 else (amount//4)+1
    avg_size = amount//amount_groups
    for i in range(0,amount_groups-len(drivers)):
        groups.append({'driver':None,'people':[]})
    # randomize list
    shuffle(people)
    for group in groups:
        for i in range(0,avg_size):
            if people:
                group['people'].append(people.pop())
        if not group['driver']:
            if direction=="hin":
                group['driver']=choice(group['people'])
                group['people'].remove(group['driver'])
                make_driver(group['driver'],day,plan)
            else:
                for person in group['people']:
                    if is_driver(plan,person,day):
                        group['driver']=person
                        group['people'].remove(group['driver'])
                        make_driver(group['driver'],day,plan)
                if not group['driver']:
                    group['driver']=choice(group['people'])
                    group['people'].remove(group['driver'])
                    make_driver(group['driver'],day,plan)
    
    return groups         

def is_driver(plan,person,day):
    driver = False
    for hour in plan[day].keys():
        for group in plan[day][hour]['hin']['groups']:
            if person==group['driver']:
                return True
        for group in plan[day][hour]['rück']['groups']:
            if person==group['driver']:
                return True
    return driver



def make_driver(person,day,plan):
    for hour in plan[day].keys():
        if person in plan[day][hour]["hin"]['people']:
            plan[day][hour]["hin"]['drivers'].append(person)
        if person in plan[day][hour]["rück"]['people']: 
            plan[day][hour]["rück"]['drivers'].append(person)

def get_avail_cars(day,time,plan):
    cars=[]
    for h in range(1,time+1):
        for driver in plan[day][h]['hin']['drivers']:
            cars.append(driver)
        for driver in plan[day][h]['rück']['drivers']:
            try:
                cars.remove(driver)
            except:
                pass
    return cars

plan = datastore.copy()
# now we gotta decide who drives with whom
for day, data in datastore.items():
    # make room to note drivers
    loners=set()
    for hour in data.keys():
        plan[day][hour]['hin'] = {'people':plan[day][hour]['hin'],"drivers":[],"groups":[]}
        plan[day][hour]['rück'] = {'people':plan[day][hour]['rück'],"drivers":[],"groups":[]}

        # whoever has to drive alone at some point becomes a driver
        if len(plan[day][hour]['hin']['people'])==1:
            loners.add(plan[day][hour]['hin']['people'][0])
        if len(plan[day][hour]['rück']['people'])==1:
            loners.add(plan[day][hour]['rück']['people'][0])
    # now we marked to people who have to drive alone in one direction, 
    # they are drivers for their other way as well
    for person in loners:
        make_driver(person,day,plan)

    # Now we gotta see if we have drivers for everything.
    # Every group driving back needs a car there

def make_plan(plan):
    #make backup_copy
    newplan=plan.copy()
    for day in newplan.keys():
        for hour in newplan["mo"].keys():
            newplan[day][hour]['hin']['groups'] = assign(newplan,day,hour,"hin")
            newplan[day][hour]['rück']['groups'] = assign(newplan,day,hour,"rück")

    return newplan         
        

if __name__=="__main__":
    myplan = make_plan(plan)
    pprint.pprint(myplan)


