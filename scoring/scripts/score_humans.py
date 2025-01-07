"""
**Scoring Human Responses**
This script calculates 2 scores (see paper) for the novice and expert humans responses.

* Unweighted Clustering Score
* Weighted Clustering Score

Assumes downloaded: beginner.csv, expert.csv, results/+{expert.json, novice.json}
Dependencies: json, pandas
"""

import json
import pandas as pd

# Function to load data from a JSON file and extract required fields
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    allwords_list = []
    score_list = []

    # Iterate through each game in the JSON data
    for game in data:
        allwords_list.append(game.get('allwords', ''))  # Get allwords, default to empty string if not found
        score_list.append(game.get('score', 0))  # Get score, default to 0 if not found

    return allwords_list, score_list

# Load data from novice.json and expert.json
novice_allwords, novice_scores = load_json_data('../../../New_LLM/novice.json')
expert_allwords, expert_scores = load_json_data('../../../New_LLM/expert.json')

# Create DataFrames for novice and expert
novice_df = pd.DataFrame({
    'Allwords': novice_allwords,
    'Unweighted Clustering Score': novice_scores
})

expert_df = pd.DataFrame({
    'Allwords': expert_allwords,
    'Unweighted Clustering Score': expert_scores
})

old_novice_df = pd.read_csv('beginner.csv')
novice_df['Weighted Clustering Score'] = old_novice_df['Total Points']

old_expert_df = pd.read_csv('expert.csv')
expert_df['Weighted Clustering Score'] = old_expert_df['Total Points']

# Display the DataFrames
print("Novice DataFrame:")
print(novice_df)
print("\nExpert DataFrame:")
print(expert_df)

# # Optionally, save to CSV files
novice_df.to_csv('../novice_scores.csv', index=True)
expert_df.to_csv('../expert_scores.csv', index=True)
