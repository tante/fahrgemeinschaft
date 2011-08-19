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
        print("%s %s on %s for hour %i" % (name,direction,days[int((i-1)/2)], hour)) 
        datastore[days[int((i-1)/2)]][hour][direction].append(name)
        print("datastore[%s][%s][%s].append(%s)" % (days[int((i-1)/2)],hour,direction,name) )
        
# now we gotta decide who drives with whom

