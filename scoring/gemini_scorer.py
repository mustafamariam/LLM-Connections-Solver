import pandas as pd


def parse_answers(file):
    """Parse the games into answer groupings
    """
    games = open(file, 'r')
    games_list = games.read().splitlines()
    game_answers = []
    # For each game separate into 4 answer categories of 4
    for game in games_list:
        l = list(game.split(", "))
        var = [l[i:i + 4] for i in range(0, len(l), 4)]
        game_answers.append(var)
    connections_answers = pd.DataFrame(game_answers[3:203])
    # Keep only 200 games
    return connections_answers


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
    answer_yellow = row[0]
    answer_green = row[1]
    answer_blue = row[2]
    answer_purple = row[3]
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
    connections_answers = parse_answers("parsedCleanedLLM.txt")
    responses_df = pd.read_csv("gemini_responses.csv")

    # Parse responses
    responses_df["Parsed Response"] = responses_df["Response"].apply(clean_gemini_response)
    # Join answers to responses df
    responses_df = responses_df.join(connections_answers, how="left", rsuffix="_answers")
    # Calculate score
    responses_df["Classification Score"] = responses_df.apply(score_gemini_response, axis=1)

    # Drop answers columns
    responses_df = responses_df.drop([0, 1, 2, 3], axis=1)
    responses_df.to_csv("gemini_responses_scored.csv", index=False)
