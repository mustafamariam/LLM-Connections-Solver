import pandas as pd


def parse_answers(file):
    """Parse the games into answer groupings
    """
    games_df = pd.read_csv(file)
    # Keep only 200 games
    games_df = games_df[3:203]
    games_df.reset_index(drop=True, inplace=True)
    # Read answers into 4 lists of 4 words
    games_df["Answers"] = games_df["Words"].apply(split_and_reshape)
    # Split 4 lists across 4 columns
    connections_answers = pd.DataFrame(games_df['Answers'].tolist(), columns=["Yellow","Green","Blue","Purple"])
    return connections_answers

def split_and_reshape(game):
    game = game.replace("'", "")
    game = game.replace('[', "")
    game = game.replace(']', "")
    split_list = game.split(', ')
    return [split_list[i:i+4] for i in range(0, len(split_list), 4)]


def clean_gemini_response(response):
    """Clean the gemini responses using brackets [] as delimiters
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
    llm_answers = []
    for s in substrings:
        l = list(s.split(","))
        # Do not add if list is more than 4
        # (this is for when the llm responds with the whole game in brackets)
        if len(l) > 4:
            continue
        # Stop at 4 groups (more is just repeats)
        if len(llm_answers) == 4:
            break
        else:
            llm_answers.append(l)
    return llm_answers


def score_gemini_response(row: pd.Series) -> pd.Series:
    response = row["Parsed Response"]
    # Each answer category is in a different columnn
    answer_yellow = row["Yellow"]
    answer_green = row["Green"]
    answer_blue = row["Blue"]
    answer_purple = row["Purple"]
    # Initialize score of game
    score = 0
    for a in response:
        # Scoring mechanism
        # If issues with response parsing of a certain game, the script will continue
        try:
            if set(a) == set(answer_yellow):
                score += 1
            if set(a) == set(answer_green):
                score += 2
            if set(a) == set(answer_blue):
                score += 3
            if set(a) == set(answer_purple):
                score += 4
        except IndexError:
            continue
    return score


if __name__ == '__main__':
    connections_answers = parse_answers("connectionsRes.csv")
    responses_df = pd.read_csv("gemini_responses.csv")

    # Parse responses
    responses_df["Parsed Response"] = responses_df["Response"].apply(clean_gemini_response)
    # Join answers to responses df
    responses_df = responses_df.join(connections_answers, how="left", rsuffix="_answers")
    # Calculate score
    responses_df["Classification Score"] = responses_df.apply(score_gemini_response, axis=1)

    # Drop answers columns
    responses_df = responses_df.drop(["Yellow", "Green", "Blue", "Purple"], axis=1)
    responses_df.to_csv("gemini_responses_scored.csv", index=False)
