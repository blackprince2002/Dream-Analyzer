import pandas as pd
import re

# Subcategories dictionary
subcategories = {
    "Perception": {
        "colour": ["red", "yellow", "blue", "green", "purple", "orange", "black", "white", "pink", "brown"],
        "hearing": ["music", "voice", "sound", "noise", "melody", "rhythm", "scream", "echo", "whisper", "humming"],
        "smell": ["fragrance", "odor", "perfume", "aroma", "scent", "stink", "smoke", "essence", "stench", "bouquet"],
        "taste": ["sweet", "bitter", "salty", "sour", "spicy", "savory", "tangy", "bland", "umami", "zesty"],
        "touch": ["soft", "rough", "smooth", "sticky", "cold", "warm", "hot", "slippery", "fuzzy", "wet"],
        "vision": ["light", "dark", "bright", "dim", "shiny", "shadow", "colorful", "gloomy", "sparkling", "blurry"],
    },
    "Emotion": {
        "anger": ["rage", "fury", "mad", "irritation", "annoyance", "hatred", "resentment", "wrath", "frustration", "agitation"],
        "happiness": ["joy", "smile", "laugh", "glee", "delight", "pleasure", "bliss", "contentment", "mirth", "cheer"],
        "fear": ["scared", "terror", "panic", "fright", "anxiety", "dread", "nervousness", "phobia", "horror", "unease"],
        "wonder": ["awe", "amazement", "curiosity", "marvel", "fascination", "intrigue", "astonishment", "admiration", "surprise", "interest"],
        "sadness": ["tears", "grief", "sorrow", "loneliness", "melancholy", "heartbreak", "despair", "mourning", "anguish", "regret"],
    },
    "Cognition": {
        "reading": ["book", "paper", "text", "novel", "story", "journal", "magazine", "article", "letter", "manuscript"],
        "writing": ["pen", "journal", "notes", "scribble", "essay", "diary", "script", "draft", "composition", "paragraph"],
        "speech": ["talking", "shouting", "whispering", "yelling", "discussion", "conversation", "dialogue", "monologue", "chanting", "debate"],
        "thinking": ["idea", "ponder", "plan", "imagine", "analyze", "reason", "dream", "reflect", "evaluate", "contemplate"],
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
        "family": ["mother", "father", "child", "brother", "sister", "parent", "son", "daughter", "grandparent", "cousin"],
        "fantastic beings": ["dragon", "elf", "ghost", "fairy", "wizard", "unicorn", "goblin", "troll", "vampire", "mermaid"],
        "female": ["woman", "girl", "her", "she", "lady", "queen", "princess", "aunt", "sister", "daughter"],
        "male": ["man", "boy", "his", "he", "king", "prince", "uncle", "brother", "father", "son"],
    },
    "Social Interactions": {
        "friendly": ["hug", "smile", "help", "wave", "greet", "chat", "handshake", "gift", "thank", "support"],
        "physical aggregation": ["fight", "punch", "hit", "kick", "grab", "push", "wrestle", "slap", "shove", "tackle"],
        "sexual": ["kiss", "intimate", "passion", "caress", "romance", "affection", "love", "embrace", "flirt", "desire"],
    },
    "Culture": {
        "architecture": ["building", "bridge", "tower", "skyscraper", "castle", "temple", "house", "palace", "cottage", "monument"],
        "art": ["painting", "sculpture", "gallery", "drawing", "mural", "portrait", "statue", "exhibition", "sketch", "design"],
        "clothing": ["shirt", "dress", "hat", "pants", "shoes", "scarf", "jacket", "coat", "belt", "gloves"],
        "food": ["bread", "meat", "fruit", "vegetable", "cake", "soup", "snack", "dessert", "drink", "cereal"],
        "money": ["cash", "coin", "salary", "wage", "banknote", "wallet", "credit", "payment", "currency", "wealth"],
        "religion": ["temple", "prayer", "god", "church", "mosque", "faith", "ritual", "holy", "belief", "spirit"],
        "school": ["classroom", "teacher", "lesson", "student", "exam", "homework", "lecture", "book", "blackboard", "assignment"],
        "sports": ["football", "cricket", "tennis", "basketball", "volleyball", "swimming", "hockey", "running", "cycling", "skiing"],
        "technology": ["computer", "robot", "phone", "laptop", "internet", "software", "gadget", "device", "AI", "VR"],
        "science": ["experiment", "lab", "theory", "research", "microscope", "physics", "biology", "chemistry", "discovery", "innovation"],
        "transportation": ["car", "train", "plane", "bus", "bike", "ship", "truck", "taxi", "tram", "subway"],
        "weapons": ["gun", "knife", "bomb", "sword", "rifle", "arrow", "pistol", "grenade", "dagger", "missile"],
    },
}


# Function to categorize a single dream
def categorize_dream(dream_text):
    categories = {}
    for category, sub_dict in subcategories.items():
        for subcategory, keywords in sub_dict.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', str(dream_text), re.IGNORECASE):
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(subcategory)
    # Remove duplicates within each category
    for cat in categories:
        categories[cat] = list(set(categories[cat]))
    return categories

# Load the cleaned dreams CSV
df = pd.read_csv('cleaned_dreams.csv')

# Categorize each dream
df['categories'] = df['dreams_text'].apply(categorize_dream)

# Save the updated dataframe to a new CSV
df.to_csv('dreams_with_categories.csv', index=False)

print("Categorized dreams have been saved to 'dreams_with_categories.csv'.")
