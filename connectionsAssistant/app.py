from flask import Flask, request, jsonify, json, render_template, session
from flask_cors import CORS 
from openai import OpenAI

# ENTER OPENAI API KEY HERE
client = OpenAI(api_key="")
description = "You are an assistant configured to solve the New York Times Connections Word game."
prompt = """
Make four groups of four words that share something in common. Categories will always be more specific than `5-LETTER-WORDS`, `NAMES` or `VERBS.`

Example 1: 
Words: ['DART', 'HEM', 'PLEAT', 'SEAM', 'CAN', 'CURE', 'DRY', 'FREEZE', 'BITE', 'EDGE', 'PUNCH', 'SPICE', 'CONDO', 'HAW', 'HERO', 'LOO']
Answer: 
```{
    "Groupings": {
        "1": {
            "Category": "Things to sew",
            "Words": [
                "DART", 
                "HEM", 
                "PLEAT", 
                "SEAM"
            ]
        },
        "2": {
            "Category": "Ways to preserve food",
            "Words": [
                "CAN", 
                "CURE", 
                "DRY", 
                "FREEZE"
            ]
        },
        "3": {
            "Category": "Sharp quality",
            "Words": [
                "BITE", 
                "EDGE", 
                "PUNCH", 
                "SPICE"
            ]
        },
        "4": {
            "Category": "Birds minus last letter",
            "Words": [
                "CONDO", 
                "HAW", 
                "HERO", 
                "LOO"
            ]
        }
    }
}```

Example 2:
Words: ['COLLECTIVE', 'COMMON', 'JOINT', 'MUTUAL', 'CLEAR', 'DRAIN', 'EMPTY', 'FLUSH', 'CIGARETTE', 'PENCIL', 'TICKET', 'TOE', 'AMERICAN', 'FEVER', 'LUCID', 'PIPE']
Answer: 
```{
    "Groupings": {
        "1": {
            "Category": "Shared",
            "Words": [
                "COLLECTIVE", 
                "COMMON", 
                "JOINT", 
                "MUTUAL"
            ]
        },
        "2": {
            "Category": "Rid of contents",
            "Words": [
                "CLEAR", 
                "DRAIN", 
                "EMPTY", 
                "FLUSH"
            ]
        },
        "3": {
            "Category": "Associated with 'stub'",
            "Words": [
                "CIGARETTE", 
                "PENCIL", 
                "TICKET", 
                "TOE"
            ]
        },
        "4": {
            "Category": "__ Dream",
            "Words": [
                "AMERICAN", 
                "FEVER", 
                "LUCID", 
                "PIPE"
            ]
        }
    }
}```

Example 3: 
Words: ['HANGAR', 'RUNWAY', 'TARMAC', 'TERMINAL', 'ACTION', 'CLAIM', 'COMPLAINT', 'LAWSUIT', 'BEANBAG', 'CLUB', 'RING', 'TORCH', 'FOXGLOVE', 'GUMSHOE', 'TURNCOAT', 'WINDSOCK']
Groupings: 
1. Parts of an airport: ['HANGAR', 'RUNWAY', 'TARMAC', 'TERMINAL']
2. Legal terms: ['ACTION', 'CLAIM', 'COMPLAINT', 'LAWSUIT']
3. Things a juggler juggles: ['BEANBAG', 'CLUB', 'RING', 'TORCH']
4. Words ending in clothing: ['FOXGLOVE', 'GUMSHOE', 'TURNCOAT', 'WINDSOCK']

Categories share commonalities:
- There will never be a miscellaneous category 
- No word will ever appear in two categories
- There will always be four words in a category
- As the category number increases, the connections between the words and their category becomes more obscure. The category 1 is the most easy and intuitive, category 4 is the hardest
- There may be a red herring category
- Category 4 often contains words with a common preposition or postposition, like the category 4 in the example

Please respond in a JSON format. Today's list of words: """

app = Flask(__name__)
CORS(app)

# ENTER SECRET KEY HERE (can be any random string)
app.secret_key = ''

@app.route("/")
def hello_world():
    return render_template("Home.html")

# process words entered with the play button
@app.route('/play', methods=['POST'])
def play():
    words = request.json['words']
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": description},
            {"role": "user", "content": prompt + words}
        ],
        max_tokens=250,
        response_format={ "type": "json_object" }
    )
    response = response.choices[0].message.content
    print(response)
    response = json.loads(response)
    response = json.dumps(response, indent=4)
    session['response'] = response
    return jsonify({"response": response})

@app.route('/answers', methods=['GET', 'POST'])
def answers():
    response = session.get('response', {})
    return render_template("Answers.html", response=response)

if __name__ == '__main__':
    app.run(debug=False, port=5000)