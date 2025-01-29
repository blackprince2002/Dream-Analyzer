from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os


app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": "*"}})  # Allow all origins for development

port = int(os.environ.get("PORT", 8080))  # Railway provides a dynamic port number
app.run(host='0.0.0.0', port=port)  # Make sure it's listening on all network interfaces

# Sentiment analysis keywords
good_keywords = [ "joy", "happiness", "wonder", "fascination", "smile", "support", "serenity", "float", "calm",
    "contentment", "bliss", "delight", "awe", "amazement", "curiosity", "marvel", "admiration", "interest",
    "glee", "pleasure", "mirth", "cheer", "harmony", "peace", "affection", "love", "embrace", "flirt", "desire",
    "friendly", "help", "hug", "chat", "thank", "greet", "handshake", "gift", "support", "positive", "warmth",
    "soft", "smooth", "warm", "bright", "shiny", "colorful", "light", "fresh", "sweet", "savory", "umami",
    "smooth", "fragrance", "scent", "fresh", "wind", "breeze", "airflow", "gentle", "soothing", "calming",
    "hope", "relief", "gratitude", "inspiration", "compassion", "trust", "respect"]
bad_keywords = [ "terror", "rage", "anger", "sadness", "death", "fight", "burn", "frustration", "fear", "scream",
    "panic", "grief", "sorrow", "loneliness", "melancholy", "heartbreak", "despair", "mourning", "anguish",
    "loss", "afterlife", "dying", "corpse", "grave", "funeral", "hate", "resentment", "wrath", "agitation",
    "fear", "nervousness", "phobia", "horror", "unease", "mad", "irritation", "annoyance", "fury", "terror",
    "fright", "anxiety", "shouting", "yelling", "argument", "dispute", "screech", "wail", "despair", "pain",
    "suffering", "danger", "threat", "violence", "hurt", "conflict", "tension", "gloom", "stink", "stench",
    "hurricane", "cyclone", "storm", "wildfire", "inferno", "blaze", "explosion", "sword", "rifle", "bomb",
    "knife", "grenade", "mine", "terrorism", "assault", "hostility", "suffering", "evil", "bloodshed", "war",
    "violence", "destruction"]

# Define the perception categories with keywords (you can expand these as needed)
categories = {
    "Perception": {
        "colour": ["red", "yellow", "blue", "green", "purple", "orange", "black", "white", "pink", "brown"],
        "hearing": ["music", "voice", "sound", "noise", "melody", "rhythm", "scream", "echo", "whisper", "humming"],
        "smell": ["fragrance", "odor", "perfume", "aroma", "scent", "stink", "smoke", "essence", "stench", "bouquet"],
        "taste": ["sweet", "bitter", "salty", "sour", "spicy", "savory", "tangy", "bland", "umami", "zesty"],
        "touch": ["soft", "rough", "smooth", "sticky", "cold", "warm", "hot", "slippery", "fuzzy", "wet"],
        "vision": ["light", "dark", "bright", "dim", "shiny", "shadow", "colorful", "gloomy", "sparkling", "blurry"],
    },
    "Emotion": {
        "anger": ["rage", "fury", "mad", "irritation", "annoyance", "hatred", "resentment", "wrath", "frustration",
                  "agitation"],
        "happiness": ["joy", "smile", "laugh", "glee", "delight", "pleasure", "bliss", "contentment", "mirth", "cheer"],
        "fear": ["scared", "terror", "panic", "fright", "anxiety", "dread", "nervousness", "phobia", "horror","fear",
                 "unease"],
        "wonder": ["awe", "amazement", "curiosity", "marvel", "fascination", "intrigue", "astonishment", "admiration",
                   "surprise", "interest"],
        "sadness": ["tears", "grief", "sorrow", "loneliness", "melancholy", "heartbreak", "despair", "mourning",
                    "anguish", "regret"],
    },
    "Cognition": {
        "reading": ["book", "paper", "text", "novel", "story", "journal", "magazine", "article", "letter",
                    "manuscript"],
        "writing": ["pen", "journal", "notes", "scribble", "essay", "diary", "script", "draft", "composition",
                    "paragraph"],
        "speech": ["talking", "shouting", "whispering", "yelling", "discussion", "conversation", "dialogue",
                   "monologue", "chanting", "debate"],
        "thinking": ["idea", "ponder", "plan", "imagine", "analyze", "reason", "dream", "reflect", "evaluate",
                     "contemplate"],
    },
    "Natural Elements": {
        "air": ["wind", "breeze", "storm", "gust", "hurricane", "cyclone", "draft", "whirlwind", "current", "airflow"],
        "earth": ["soil", "rock", "sand", "mud", "clay", "pebble", "gravel", "mountain", "hill", "valley"],
        "fire": ["flame", "burn", "ash", "blaze", "inferno", "spark", "ember", "smoke", "torch", "wildfire"],
        "water": ["river", "ocean", "rain", "lake", "stream", "wave", "sea", "pond", "waterfall", "tide"],
    },
    "Movement": {
        "death": ["dying", "dead", "corpse", "funeral", "grave", "passing", "loss", "afterlife", "mourning", "end"],
        "falling": ["drop", "collapse", "plunge", "tumble", "descend", "slip", "stumble", "crash", "dive", "topple"],
        "flying": ["soar", "glide", "hover", "float", "ascend", "drift", "takeoff", "pilot", "flap", "airborne"],
        "walking": ["stroll", "march", "stride", "amble", "wander", "hike", "saunter", "trek", "pace", "roam"],
        "running": ["sprint", "dash", "jog", "rush", "hurry", "race", "chase", "gallop", "bolt", "charge"],
    },
    "Characters": {
        "animals": ["dog", "cat", "lion", "tiger", "bear", "rabbit", "snake", "bird", "fish", "elephant"],
        "family": ["mother", "father", "child", "brother", "sister", "parent", "son", "daughter", "grandparent",
                   "cousin"],
        "fantastic beings": ["dragon", "elf", "ghost", "fairy", "wizard", "unicorn", "goblin", "troll", "vampire",
                             "mermaid"],
        "female": ["woman", "girl", "her", "she", "lady", "queen", "princess", "aunt", "sister", "daughter"],
        "male": ["man", "boy", "his", "he", "king", "prince", "uncle", "brother", "father", "son"],
    },
    "Social Interactions": {
        "friendly": ["hug", "smile", "help", "wave", "greet", "chat", "handshake", "gift", "thank", "support"],
        "physical aggregation": ["fight", "punch", "hit", "kick", "grab", "push", "wrestle", "slap", "shove", "tackle"],
        "sexual": ["kiss", "intimate", "passion", "caress", "romance", "affection", "love", "embrace", "flirt",
                   "desire"],
    },
    "Culture": {
        "architecture": ["building", "bridge", "tower", "skyscraper", "castle", "temple", "house", "palace", "cottage",
                         "monument"],
        "art": ["painting", "sculpture", "gallery", "drawing", "mural", "portrait", "statue", "exhibition", "sketch",
                "design"],
        "clothing": ["shirt", "dress", "hat", "pants", "shoes", "scarf", "jacket", "coat", "belt", "gloves"],
        "food": ["bread", "meat", "fruit", "vegetable", "cake", "soup", "snack", "dessert", "drink", "cereal"],
        "money": ["cash", "coin", "salary", "wage", "banknote", "wallet", "credit", "payment", "currency", "wealth"],
        "religion": ["temple", "prayer", "god", "church", "mosque", "faith", "ritual", "holy", "belief", "spirit"],
        "school": ["classroom", "teacher", "lesson", "student", "exam", "homework", "lecture", "book", "blackboard",
                   "assignment"],
        "sports": ["football", "cricket", "tennis", "basketball", "volleyball", "swimming", "hockey", "running",
                   "cycling", "skiing"],
        "technology": ["computer", "robot", "phone", "laptop", "internet", "software", "gadget", "device", "AI", "VR"],
        "science": ["experiment", "lab", "theory", "data", "hypothesis", "discovery", "research", "physics",
                    "chemistry", "biology"],
        "transportation": ["car", "train", "bus", "airplane", "bicycle", "ship", "subway", "boat", "plane",
                           "helicopter"],
        "weapons": ["gun", "rifle", "sword", "pistol", "bomb", "explosion", "knife", "bullet", "grenade", "mine"],
    }
}

# Precompile category patterns
category_patterns = {}
for category, subcats in categories.items():
    category_patterns[category] = {}
    for subcat, keywords in subcats.items():
        category_patterns[category][subcat] = [
            re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE) for kw in keywords
        ]

def classify_dream(text):
    # Sentiment analysis
    good_count = sum(1 for pattern in good_patterns if pattern.search(text))
    bad_count = sum(1 for pattern in bad_patterns if pattern.search(text))
    
    sentiment = "Neutral"
    if good_count > bad_count:
        sentiment = "Positive"
    elif bad_count > good_count:
        sentiment = "Negative"

    # Category analysis
    results = {}
    for category, subcats in category_patterns.items():
        category_results = {}
        for subcat, patterns in subcats.items():
            matches = []
            for pattern in patterns:
                if pattern.search(text):
                    matches.append(pattern.pattern.replace(r'\b', '').replace('(?i)', '').lower())
            if matches:
                category_results[subcat] = list(set(matches))
        if category_results:
            results[category] = category_results
            
    return sentiment, results

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'dream' not in data:
            return jsonify({"error": "Missing dream text"}), 400
        
        text = data['dream'].lower()
        sentiment, categories = classify_dream(text)
        
        return jsonify({
            "sentiment": sentiment,
            "categories": categories
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
