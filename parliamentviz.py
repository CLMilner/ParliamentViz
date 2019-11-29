#Any feedback or ideas for exapanding gratefully received

import sqlite3
import numpy as np
import matplotlib.pyplot as plt



conn = sqlite3.connect('mpdatabase.sqlite')
cur = conn.cursor()


conn = sqlite3.connect('mpdatabase.sqlite')
cur = conn.cursor()

#User will choose the year to see the split by gender by party

year = input('Enter year: ')

#Query to get number of parties. Order by count.
#In an election year, we will take the numbers from the incoming parliament since this would be most useful.

cur.execute(
(('''SELECT party.party, Count(*)
FROM MP
JOIN Gender JOIN Party Join Startyear Join Endyear on mp.gender_id=gender.id and mp.party_id=party.id and mp.startyear_id=startyear.id and mp.endyear_id=endyear.id
where startyear <=''')+(year)+(''' and endyear >''')+(year)+
(''' Group by party.party Order by count(*) desc''')))


chartdata = cur.fetchall()
#print(chartdata)

#Create dictionary for party names, males and female counts
partynames = {}
for i in chartdata:
	partyname = i[0]
	partynames[partyname] = {'Male': 0, 'Female': 0}
#print(partynames)

#Query number of males and asign to dictionary
cur.execute(
(('''SELECT party.party, Count(*)
FROM MP
JOIN Gender JOIN Party Join Startyear Join Endyear on mp.gender_id=gender.id and mp.party_id=party.id and mp.startyear_id=startyear.id and mp.endyear_id=endyear.id
where gender.gender="Male" and startyear <=''')+(year)+(''' and endyear >''')+(year)+
(''' Group by party.party''')))


males = cur.fetchall()

for i in males:
	x = i[0]
	partynames[x]['Male'] = (i[1])
#print(partynames)

#Query number of females and assign to dictionary

cur.execute(
(('''SELECT party.party, Count(*)
FROM MP
JOIN Gender JOIN Party Join Startyear Join Endyear on mp.gender_id=gender.id and mp.party_id=party.id and mp.startyear_id=startyear.id and mp.endyear_id=endyear.id
where gender.gender="Female" and startyear <=''')+(year)+(''' and endyear >''')+(year)+
(''' Group by party.party''')))


females = cur.fetchall()

for i in females:
	x = i[0]
	partynames[x]['Female'] = (i[1])
print(partynames)


# Close database connection
conn.close()

import numpy as np
import matplotlib.pyplot as plt



all_party = []
all_men = []
all_women = []

for i in partynames:
	all_party.append(i)
	all_men.append(partynames[i]['Male'])
	all_women.append(partynames[i]['Female'])


#The total list of parties is too long for charting, so this chooses main parties to compare.
#Create list of the top 3 parties.

select_party = []
select_party.append(chartdata[0][0])
select_party.append(chartdata[1][0])
select_party.append(chartdata[2][0])

#print(select_party)

select_men = []
select_women = []
for i in select_party:
	select_men.append(partynames[i]['Male'])
	select_women.append(partynames[i]['Female'])
#print(select_men)
#print(select_women)

#Create 'other' category for grouping all other partys together
select_party.append("All other parties")
print(select_party)
N = ((len(select_party)))

#Calculate total men & women in all other partys and append to list for chart
other_men = sum(all_men)-sum(select_men)
other_women = sum(all_women)-sum(select_women)
select_men.append(other_men)
select_women.append(other_women)
print(select_men)
print(select_women)

#print(all_party, all_men, all_women)

ind = np.arange(N)    # the x locations for the groups, if all parties use 'N'
width = 0.2       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, select_men, width)
p2 = plt.bar(ind, select_women, width,
             bottom=select_men)

plt.ylabel('Parties')
plt.title(('Parties by gender in '+ year))
plt.xticks(ind, select_party)
total = int(sum(all_men)+sum(all_women)) # to get sensible axis length by taking average party size
step = int(total/10)
plt.yticks(np.arange(0, total, step)) #where x1 is bottom label on axis, x2 is top of axis, and x3 is gap between values
plt.legend((p1[0], p2[0]), ('Men', 'Women'))

plt.show()
