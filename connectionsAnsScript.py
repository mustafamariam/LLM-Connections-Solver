from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import sys
import csv
import pandas as pd

# txt = "/Users/mariammustafa/COMS3997LLM/connDataSample.rtf"
txt = "/Users/mariammustafa/COMS3997LLM/connections-ans copy.txt"
target = " - "
#bullets = ["\uc0\u9702", "\'95    ", "	◦	", "	◦	"]
arr = ""
with open(txt, "r") as file:
    data = file.read()

#reformatting answers, can comment out 18-25 after running once

with open(txt, "w") as file:
    #cleaning answer file for later parsing purposes
    file.write(data.replace(target, ": "))
    # for b in bullets:
    #     file.write(data.replace(b, ""))

with open(txt, "r") as file:
    data = file.read()

file1 = open(txt, 'r')
Lines = file1.readlines()
 
arr = []
cat = []

# only including lines with Connections answers
for line in Lines:
    if "2024" not in line and "2023" not in line:
        line = line.split(':')
        arr.append(line[len(line)-1])
        #connections categories list
        if '◦' in line[0]:
            line[0] = line[0].replace('◦', "")
        cat.append(line[0].strip())

#print(arr)
file1.close()

clean = []

# writing individual words to array of answers
for i in arr:
        #print(type(i))
        x =i.split(", ")
        for y in x:
            y1=y.replace("\\\n","")
            if "}" in y:
                y1=y1.replace("}","")
            y1 = y.replace("'", "")
            clean.append(y1.strip())

#print(clean)
            
#writing list of Connection answers
f = open("cleanedLLM.txt", "a")
f.write(str(clean))
f.close()

#splitting arrays into 16 (answers for each day)
sub = []    
for i in range(0, len(clean)-15, 16):
     sub.append(clean[i:i+16])

#creating txt file of 16 items per row
f = open("parsedCleanedLLM.txt", "a")
for i in sub:
     f.write(str(i)[1:-1].replace("'", ""))
     f.write('\n')
f.close()

#writing entire list of categories to txt file
f = open("catLST.txt", "a")
f.write(str(cat))
f.close()
     
#putting categories and answers in CSV
headers = ["Answers (16)"]
with open("connectionsRes.csv", 'w') as csvfile:
     csvwriter = csv.writer(csvfile, delimiter=',')

     #creating a header
     csvwriter.writerow(headers)
     #write data to csv
     csvwriter.writerow(sub)

#transpose rows to columns at the end in Excel

with open("categoriesConn.csv", 'w') as csvfile:
     csvwriter = csv.writer(csvfile, delimiter=',')

     #write data to csv
     csvwriter.writerow(cat)

#transpose rows to columns at the end in Excel
