import openai
import csv
import anthropic
import google.generativeai as genai

# Add your api keys
openai.api_key = ""
gemini_api_key = ""
claude_api_key = ""
llama_api_key = ""


def open_games(games_file):
    """Open games file, read each game onto a new line, and shuffle game.
    """
    games = open(games_file, 'r')
    games_list = games.read().splitlines()
    games_list_shuffled = list()
    for game in games_list:
        l = list(game.split(", "))
        random.shuffle(l)
        games_list_shuffled.append(', '.join(l))
    return games_list_shuffled


def open_prompt(prompt_file):
    """Open prompt text file.
    """
    prompt_file = open(prompt_file, 'r')
    return prompt_file.read()


def run_chatgpt(prompt, api_key):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}, ],
        max_tokens=750,
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
        max_tokens=750,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


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
        for n in range(3, 203):
            game_prompt = prompt.replace("InsertGame", games[n])
            response = play(game_prompt, api_key)
            response.replace("\n", " ")
            writer.writerow([response])


if __name__ == '__main__':
    games_list = open_games('parsedCleanedLLM.txt')
    prompt = open_prompt("prompt.txt")
    # Run chat-gpt 4o
    run_games(games_list, "chatgpt_responses.csv", run_chatgpt, openai.api_key)
    # Run gemini
    # run_games(games_list, "gemini_responses.csv", run_gemini, gemini_api_key)
    # Run Claude
    # run_games(games_list, "claude_responses.csv", run_claude, claude_api_key)
    # Run Llama
    # run_games(games_list, "llama_responses.csv", run_llama, llama_api_key)

