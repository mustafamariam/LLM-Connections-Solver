import json

def find_intersection(list1, list2):
    # Convert inner lists to sets for efficient comparison
	set1 = [set(sublist) for sublist in list1]
	set2 = [set(sublist) for sublist in list2]
    
	intersection = [list(s1) for s1 in set1 if s1 in set2]
	return intersection

with open('gold_data.json') as f:
	data = json.load(f)

exclude_list = []
gold = {}
for elem in data:
	if 'exclude' in elem:
		exclude_list.append(elem['allwords'])
		continue
	gold[elem['allwords']] = elem['categories']

win_rate = {'gpt4o': {0:0,1:0,2:0,3:0,4:0},'claude': {0:0,1:0,2:0,3:0,4:0},'llama3.1405B': {0:0,1:0,2:0,3:0,4:0},
'gemini': {0:0,1:0,2:0,3:0,4:0},'mistral': {0:0,1:0,2:0,3:0,4:0}}

for model in ['gpt4o','claude3.5sonnet','llama3.1405B','gemini1.5pro.json','mistral2large']:
	with open(model+'.json') as f:
		data = json.load(f)
	for game in data:
		if game['allwords'] in exclude_list:
			continue
		gold_categories = [sorted(gold[game['allwords']][cat]) for cat in gold[game['allwords']]]
		pred_categories = [sorted(game['categories'][cat]) for cat in game['categories']]
		intersection = find_intersection(gold_categories,pred_categories)
		if len(intersection)==0:
			print(model,game['allwords'])
		win_rate[model][len(intersection)] = win_rate[model][len(intersection)]+1


for model in win_rate:
	print(model, win_rate[model])
