'''
**Claude Scoring Script**

This script scores Claude's Connections answers.

*   Collects Claude's answer groupings.
*   Scores groupings for accuracy according to the provided scoring schema. 

Assumes input CSV file: `claude_responses.csv`
Dependencies: `csv`, `re`, `collections`

'''

import csv
import re
from collections import defaultdict

'''
Helper function to get answer groupings 
Parameters: answer_text (string)
Returns: groupings (list of sets)
'''
def extract_answers(answer_text):
    groupings = []
    
    # Create pattern to match groupings section
    pattern = re.compile(r'(\w+(?: \w+)*): \[([A-Z, ]+)\]')
    
    # Find all answers
    matches = pattern.findall(answer_text)

    # Create list of sets
    for match in matches:
        category, words = match
        words_set = set(words.split(", "))
        groupings.append(words_set)
    
    return groupings

'''
Gets all Claude's answer groupings 
Parameters: filename (path to .csv file)
Returns: all groupings (list of lists of sets)
'''
def get_claude_answers(filename):
    all_groupings = []
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)

        # Skip header
        next(reader, None)

        # Read .csv file
        for row in reader:
            if row:
                text = row[0]
                extracted_groupings = extract_answers(text)
                
                # Create list of collected sets
                if len(extracted_groupings) == 4 and all(len(group) == 4 for group in extracted_groupings):
                    all_groupings.append(extracted_groupings)

    return all_groupings