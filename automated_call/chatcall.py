"""
**Automated Calling of LLMs**
This script conducts automated calls of the LLMs with our prompt for 200 games.

*   Calls 4 LLMs: ChatGPT 4o, Gemini, Claude 3 opus, and Llama

Assumes downloaded: prompt.txt, parsedCleanedLLM.txt
Dependencies: openai, csv, anthropic, google-generativeai, pandas
"""

import openai
import random
import csv
import anthropic
import google.generativeai as genai
import pandas as pd

# Add your api keys
openai.api_key = ""
gemini_api_key = ""
claude_api_key = ""
llama_api_key = ""


def open_games(games_file):
    """Open games file, read each game onto a new line, and shuffle game.
    """
    games_df = pd.read_csv(games_file)
    # Read answers into 4 lists of 4 words
    games_df["Words"] = games_df["Words"].apply(split_and_reshape)
    games_list = games_df["Words"].tolist()
    return games_list

def split_and_reshape(game):
    """ Read rows of csv in into list, shuffle, and then convert back to string
    """
    game = game.replace("'", "")
    game = game.replace('[', "")
    game = game.replace(']', "")
    # Convert words to list of words
    game = list(game.split(", "))
    # Shuffle words
    random.shuffle(game)
    # Convert to string
    game = ', '.join(game)
    return game


def open_prompt(prompt_file):
    """Open prompt text file.
    """
    prompt_file = open(prompt_file, 'r')
    return prompt_file.read()


def run_chatgpt(prompt, api_key):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}, ],
        max_tokens=300,
    )
    return response.choices[0].message.content


def run_gemini(prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text


def run_claude(prompt, api_key):
    client = anthropic.Anthropic(api_key=api_key,)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content


def run_llama(prompt, api_key):
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.llama-api.com"
    )
    response = client.chat.completions.create(
        model="llama-13b-chat",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content


def run_games(games, filename, play, api_key):
    """Run model (based on play function) with prompt.
    New game will be inserted into prompt string.
    """
    with open(filename, mode='w', newline='') as file:
        # Create a csv.writer object
        writer = csv.writer(file)
        # Exclude demonstration games that appear in prompt (first 3 rows) and run 200 games
        for n in range(3, 5):
            game_prompt = prompt.replace("InsertGame", games[n])
            response = play(game_prompt, api_key)
            response.replace("\n", " ")
            writer.writerow([response])


if __name__ == '__main__':
    games_list = open_games('connectionsRes.csv')
    prompt = open_prompt("prompt.txt")
    # Run chat-gpt 4o
    run_games(games_list, "chatgpt_responses.csv", run_chatgpt, openai.api_key)
    # Run gemini
    # run_games(games_list, "gemini_responses.csv", run_gemini, gemini_api_key)
    # Run Claude
    # run_games(games_list, "claude_responses.csv", run_claude, claude_api_key)
    # Run Llama
    # run_games(games_list, "llama_responses.csv", run_llama, llama_api_key)
