'''
**LLM Scoring Script**

This script scores Connections answers from the LLM responses.

*   Collects answer groupings from the connectionsRes.csv
*   Parses LLM responses
*   Scores groupings for accuracy according to the provided scoring schema.

Assumes input CSV file: `gemini_responses.csv`, `claude_responses.csv`, `chatgpt_responses`, `llama_responses`
Outputs 4 CSV files for each LLM with parsed responses and clustering score in new columns
Dependencies: `pandas`
'''

import pandas as pd


def parse_answers(file):
    """Parse the games into answer groupings
    Parameters: filename (path to connectionsRes.csv)
    Returns: df with each group of a game in a different column of the same row
    """
    games_df = pd.read_csv(file)
    # Keep only 200 games
    games_df = games_df[3:203]
    games_df.reset_index(drop=True, inplace=True)
    # Read answers into 4 lists of 4 words
    games_df["Answers"] = games_df["Words"].apply(split_and_reshape)
    # Split 4 lists across 4 columns
    answers_df = pd.DataFrame(games_df['Answers'].tolist(), columns=["Yellow","Green","Blue","Purple"])
    return answers_df


def split_and_reshape(game):
    """Read rows into list of 4 lists of 4 words
    Parameters: row of answers df
    Returns: list of 4 lists of 4 words (each answer category is a list within the list)
    """
    game = game.replace("'", "")
    game = game.replace('[', "")
    game = game.replace(']', "")
    split_list = game.split(', ')
    return [split_list[i:i+4] for i in range(0, len(split_list), 4)]


def clean_response(response):
    """Clean the LLM responses using brackets [] as delimiters
    Parameters: String of llm responses (one cell in responses df)
    Returns: Cleaned response as list of 4 lists of 4 words
    """
    substrings = []
    split_str = response.split("[")
    for s in split_str[1:]:
        split_s = s.split("]")
        if len(split_s) > 1:
            r = split_s[0].replace("'", "")
            r = r.replace(" ", "")
            substrings.append(r)
    # Create a list of lists of the answer groupings (each category is a different substring)
    formatted_groupings = []
    for s in substrings:
        l = list(s.split(","))
        # Do not add if list is more than 4
        # (this is for when the llm responds with the whole game in brackets)
        if len(l) > 4:
            continue
        # Stop at 4 groups (more is just repeats)
        if len(formatted_groupings) == 4:
            break
        else:
            formatted_groupings.append(l)
    return formatted_groupings


def score_response(row: pd.Series):
    """Calculates Clustering scores of responses according to our scoring schema
    * Scoring Schema Weighted Clustering Score *
    - Yellow Category (+1), Green Category (+2), Blue Category (+3), Purple Category (+4)
    - Maximum Clustering Score = 10, Minimum Clustering Score = 0
    - Score of 99 means calculate this score manually
    Parameters: Parsed LLM response
    Returns: Clustering scores
    """
    response = row["Parsed Response"]
    # Each answer category is in a different column
    answer_yellow = row["Yellow"]
    answer_green = row["Green"]
    answer_blue = row["Blue"]
    answer_purple = row["Purple"]
    # Initialize scores of game
    weighted_cscore = 0
    c_score = 0
    for a in response:
        # Scoring mechanism
        try:
            if set(a) == set(answer_yellow):
                weighted_cscore += 1
                c_score += 1
            if set(a) == set(answer_green):
                weighted_cscore += 2
                c_score += 1
            if set(a) == set(answer_blue):
                weighted_cscore += 3
                c_score += 1
            if set(a) == set(answer_purple):
                weighted_cscore += 4
                c_score += 1
        except IndexError:
            # If error, flag to score manually and continue
            weighted_cscore = 99
            continue
    return pd.Series({ "Weighted Clustering Score": weighted_cscore,
                       "Unweighted Clustering Score": c_score})


def create_scored_df(answers_df, responses_file):
    """Parse and score llm responses
    Parameters: df returned by parse_answers(), path to llm response file
    Returns: df with original response, parsed response, and clustering score columns
    """
    # Read and prepare responses_file
    responses_df = pd.read_csv(responses_file, header=None)
    responses_df.columns = ['Response']

    # Parse responses
    responses_df["Parsed Response"] = responses_df["Response"].apply(clean_response)
    # Join answers_df to responses df
    responses_df = responses_df.join(answers_df, how="left", rsuffix="_answers")
    # Calculate scores
    responses_df[["Weighted Clustering Score", "Unweighted Clustering Score"]] = responses_df.apply(score_response, axis=1)
    # Drop answers columns
    responses_df = responses_df.drop(["Yellow", "Green", "Blue", "Purple"], axis=1)

    return responses_df


if __name__ == '__main__':
    answers_df = parse_answers("reasoning/connectionsRes.csv")
    # Gemini
    gemini_scored_responses_df = create_scored_df(answers_df, "responses/gemini_responses.csv")
    gemini_scored_responses_df.to_csv("gemini_scored.csv", index=False)
    # Claude
    claude_scored_responses_df = create_scored_df(answers_df, "responses/claude_responses.csv")
    claude_scored_responses_df.to_csv("claude_scored.csv", index=False)
    # GPT4-o
    chatgpt_scored_responses_df = create_scored_df(answers_df, "responses/chatgpt_responses.csv")
    chatgpt_scored_responses_df.to_csv("gpt_scored.csv", index=False)
    # Llama
    llama_scored_responses_df = create_scored_df(answers_df, "responses/llama_responses.csv")
    llama_scored_responses_df.to_csv("llama_scored.csv", index=False)
