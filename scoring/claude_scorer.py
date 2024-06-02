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
import pandas as pd

'''
Helper function to get answer groupings 
Parameters: answer_text (string)
Returns: groupings (list of sets)
'''
def extract_groupings(answer_text):
    # Searches for "Groupings:" pattern
    pattern = r"\s*Groupings\s*:\s*(.*?)(?=Groupings\s*:|\Z)"
    matches = re.search(pattern, answer_text, re.MULTILINE | re.DOTALL)
    if matches:
        groupings_text = matches.group(1)
        group_pattern = r"([\w\s]+?)\s*:\s*\[([\w\s,]+)\]"
        group_matches = re.findall(group_pattern, groupings_text)
        formatted_groupings = []
        for group_name, group_items in group_matches:
            items = [item.strip() for item in group_items.split(',')]
            formatted_groupings.append(items)
        return formatted_groupings
    else:
        return None

'''
Gets all Claude's answer groupings 
Parameters: filename (path to .csv file)
Returns: pandas dataframe of Responses & Parsed Responses
'''
def create_claude_responses_df(input_file):
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    data = {'Response': [], 'Parsed Response': []}

    for row in rows:
        original_text = row[0]
        groupings = extract_groupings(row[0])
        cleaned_response = repr(groupings) if groupings else ""
        data['Response'].append(original_text)
        data['Parsed Response'].append(cleaned_response)

    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
  df = create_claude_responses_df("claude_responses.csv")
  df.to_csv("temp_claude_output.csv")
