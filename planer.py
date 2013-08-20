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

sequence= ["mo","di","mi","do","fr"]

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
oneway = []
allpeople = []
for row in reader:
    name = row[0]
    allpeople.append(name)
    for i in range(1,11):
        direction = "hin" if i%2 else "rück"
        try:
            hour = int(row[i])
            if hour!=-1:
                datastore[days[int((i-1)/2)]][hour][direction].append(name)
            else:
                oneway.append([name,str(days[int((i-1)/2)])])
        except:
            pass

def assign(plan,day,hour,direction):
    people = list(set(plan[day][hour][direction]["people"]))
    drivers = list(set(plan[day][hour][direction]["drivers"]))
    groups=[]
    amount = len(people)
    if not people:
        return []
    for person in drivers:
        groups.append({'driver':person,'people':[]})
        people.remove(person)
    if not people:
        return groups
    amount_groups = amount//4 if amount%4==0 else (amount//4)+1
    avg_size = amount//amount_groups
    for i in range(0,amount_groups-len(drivers)):
        groups.append({'driver':None,'people':[]})
    # randomize list
    shuffle(people)
    for group in groups:
        #        for i in range(0,avg_size):
        for i in range(0,4):
            if people:
                if len(group['people'])<3:
                    group['people'].append(people.pop())
        if not group['driver']:
            if direction=="hin":
                group['driver']=choice(group['people'])
                group['people'].remove(group['driver'])
                make_driver(group['driver'],day,plan)
            else:
                for person in group['people']:
                    if drove_to_work(plan,person,day):
                        group['driver']=person
                        group['people'].remove(group['driver'])
                        make_driver(group['driver'],day,plan)
                    else:
                        pass
                        #print("No clue who to make driver")
                if not group['driver']:
                    group['driver']=choice(group['people'])
                    group['people'].remove(group['driver'])
                    make_driver(group['driver'],day,plan)
    while people:
        for group in groups:
            if len(group['people'])<4:
                groups[groups.index(group)]['people'].append(people.pop())
                break

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

def add_group(plan,day,hour,direction,driver):
    for group in plan[day][hour][direction]['groups']:
        if driver in group["people"]:
            plan[day][hour][direction]["groups"][plan[day][hour][direction]["groups"].index(group)]['people'].remove(driver)
    plan[day][hour][direction]["groups"].append({'driver':driver,'people':[]})

def make_driver(person,day,plan,one=False):
    for hour in plan[day].keys():
        if person in plan[day][hour]["hin"]['people']:
            plan[day][hour]["hin"]['drivers'].append(person)
        if person in plan[day][hour]["rück"]['people']: 
            plan[day][hour]["rück"]['drivers'].append(person)
        for group in plan[day][hour]["hin"]['groups']:
            if person in group['people']:
                add_group(plan,day,hour,"hin",person)

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
for one in oneway:
    make_driver(one[0],one[1],plan)


def make_plan(plan):
    #make backup_copy
    newplan=plan.copy()
    for day in newplan.keys():
        for hour in newplan["mo"].keys():
            newplan[day][hour]['hin']['groups'] = assign(newplan,day,hour,"hin")
            newplan[day][hour]['rück']['groups'] = assign(newplan,day,hour,"rück")
    return newplan         

def drove_to_work(plan,person,day):
    output=False
    for hour in plan[day].keys():
        for group in plan[day][hour]['hin']['groups']:
            if person==group['driver']:
                return True
    return False

def check_consistency(plan):
    # we consider the plan to be fine until we find out differently
    output = [True,"Everything fine"]
    for day in plan.keys():
        for hour in plan[day].keys():
            for group in plan[day][hour]["hin"]['groups']:
                if not group['driver']:
                    return [False,"Group has no driver"]
   #         for group in plan[day][hour]["rück"]['groups']:
  #              if not drove_to_work(plan,group['driver'],day):
   #                 return [False,"Person driving back did not drive to work (%s %i person: %s)" % (day,hour,group['driver']) ]
            for person in plan[day][hour]["hin"]['people']:
                ontheirway = False
                for group in plan[day][hour]["hin"]['groups']:
                    if (person in group['people']) or person==group['driver']:
                        ontheirway=True
                if not ontheirway:
                    return [False,"Person not on their way to work (%s %i person: %s)" % (day,hour,person) ]
                    
            for person in plan[day][hour]["rück"]['people']:
                ontheirway = False
                for group in plan[day][hour]["rück"]['groups']:
                    if (person in group['people']) or person==group['driver']:
                        ontheirway=True
                if not ontheirway:
                    return [False,"Person not on their way back home (%s %i person: %s)" % (day,hour,person) ]
    # niemand soll häufiger als 3 mal fahren
    #for person in allpeople:
    #    isdriver = 0
    #    for day in sequence:
    #        if drove_to_work(plan,person,day):
    #            isdriver +=1
    #    if isdriver>3:
    #        return [False,"%s fährt häufiger als 3 mal" % person]
            
    return output


def write(plan,filename):
    sequence = ["mo","di","mi","do","fr"]
    writer = csv.writer(open(filename,"w"), dialect='excel')
    writer.writerow([None,"Montag","Dienstag","Mittwoch","Donnerstag","Freitag"])
    for hour in range(1,10):
        togroups = []
        backgroups = []
        for day in sequence:
            togroups.append(plan[day][hour]['hin']['groups'])
            backgroups.append(plan[day][hour]['rück']['groups'])
        line = [hour]
        for day in sequence:
            line.append(mergeoutput(togroups[sequence.index(day)],backgroups[sequence.index(day)]))
        writer.writerow(line)

def formatgroup(group,direction):
    string = ""
    if direction=="hin":
        string += "→"
    else:
        string += "←"
    string += group['driver']
    string += ", "
    string += ", ".join(group['people'])
    return string

def mergeoutput(togroups,backgroups):
    string= ""
    for group in togroups:
        string+=formatgroup(group,"hin")
        string+="\n"
    for group in backgroups:
        string+=formatgroup(group,"rück")
        string+="\n"
    return string


if __name__=="__main__":
    planOK = False
    while not planOK:
        myplan = make_plan(plan)
        planOK, message = check_consistency(myplan)
        if not planOK:
            print("Fehler:")
            print(message)
    
#    for day in sequence:
 #       print(day.upper())
  #      pprint.pprint(myplan[day])
    
    write(myplan,"test.csv")

