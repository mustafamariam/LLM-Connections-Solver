import json
import pandas as pd

def find_intersection(list1, list2):
    # Convert inner lists to sets for efficient comparison
    set1 = [set(sublist) for sublist in list1]
    set2 = [set(sublist) for sublist in list2]
    intersection = [list(s1) for s1 in set1 if s1 in set2]
    return intersection

def calculate_weighted_clustering(gold_categories, pred_categories):
    weighted_score = 0

    # Check if pred_categories is a dictionary
    if not isinstance(pred_categories, dict):
        print("Skipping non-dictionary input for pred_categories.")
        return weighted_score  # Return 0 if not a dictionary

    # Convert the category lists to sets for easier comparison
    gold_values = [set(values) for values in gold_categories.values()]

    # Check if gold_categories is a dictionary
    if not isinstance(gold_categories, dict):
        print("Skipping non-dictionary input for gold_categories.")
        return weighted_score  # Return 0 if not a dictionary

    pred_values = [set(values) for values in pred_categories.values()]

    # Iterate through gold values and check if they exist in pred values
    for i, gold_set in enumerate(gold_values):
        if gold_set in pred_values:  # Check if the same set exists in the model data
            weighted_score += (i + 1)  # Add (i + 1) to get the correct weight for each category

    return weighted_score


# Load the gold data
with open('gold_data.json') as f:
    gold_data = json.load(f)

# Prepare exclude list and gold dictionary
exclude_list = []
gold = {}
for elem in gold_data:
    if 'exclude' in elem:
        exclude_list.append(elem['allwords'])
        continue
    gold[elem['allwords']] = elem['categories']

# Iterate over the model files
for model in ['gpt4o', 'claude3.5sonnet', 'llama3.1405B', 'gemini1.5pro', 'mistral2large']:
    # Load the model's prediction data
    with open(model + '.json') as f:
        model_data = json.load(f)

    # Create an empty list to store rows for the DataFrame
    df_rows = []

    # Iterate through each game in the model data
    for game in model_data:
        if game['allwords'] in exclude_list:
            continue

        # Get gold categories and predicted categories
        gold_categories = gold[game['allwords']]
        model_categories = game['categories']

        # Debugging output to check the structure
        print(f"Gold Categories: {gold_categories}")
        print(f"Model Categories: {model_categories}")

        # Calculate the number of intersections
        gold_categories_list = [sorted(gold[game['allwords']][cat]) for cat in gold[game['allwords']]]
        pred_categories_list = [sorted(game['categories'][cat]) for cat in game['categories']]
        intersection = find_intersection(gold_categories_list, pred_categories_list)
        num_intersections = len(intersection)

        # Calculate the weighted clustering score
        weighted_clustering_score = calculate_weighted_clustering(gold_categories, model_categories)

        # Check if 'categorical_score' exists and count "Yes"
        if 'categorical_score' in game:
            categorical_score = game['categorical_score']
            categorical_reasoning_score = sum(1 for score in categorical_score.values() if score == "Yes")
        else:
            print(f"Warning: 'categorical_score' missing for game: {game['allwords']}")
            categorical_reasoning_score = 0  # or set to another default value

        # Append the game info and scores to the list of rows
        df_rows.append({
            'Allwords': game['allwords'],
            'Unweighted Clustering Score': num_intersections,
            'Weighted Clustering Score': weighted_clustering_score,
            'Categorical Reasoning Score': categorical_reasoning_score
        })


    # Create a DataFrame from the rows
    df = pd.DataFrame(df_rows)

    # Save the DataFrame to a CSV file, including the index
    df.to_csv(f'{model}_scores.csv', index=True)

    # Print or inspect the DataFrame for the current model (optional)
    print(f"DataFrame for {model} created with {len(df)} entries.")
