import streamlit as st
import time
import os
import sys
import re  # Added missing import
from streamlit_extras.let_it_rain import rain
from PIL import Image
import base64

# Load your logo image (replace 'logo.png' with your actual file path)
logo_path = r"logo.png"
logo_image = Image.open(logo_path)


# Convert image to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


logo_base64 = image_to_base64(logo_path)

# Add CSS styling
st.markdown("""
    <style>
    .powered-by {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 15px;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-size: 18px;
        color: white;
    }
    .logo-img {
        height: 80px;
        width: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Define good and bad keywords for sentiment analysis
# Define good and bad keywords for sentiment analysis
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


# Sentiment classification function
def classify_sentiment(dream_text):
    good_matches = [word for word in good_keywords if re.search(r'\b' + word + r'\b', dream_text.lower())]
    bad_matches = [word for word in bad_keywords if re.search(r'\b' + word + r'\b', dream_text.lower())]

    if len(good_matches) > len(bad_matches):
        return "Positive", good_matches, bad_matches
    elif len(bad_matches) > len(good_matches):
        return "Negative", good_matches, bad_matches
    else:
        return "Neutral", good_matches, bad_matches


# Category classification function
def classify_category(dream_text):
    categories_found = {}
    for category, keywords_dict in categories.items():
        for subcategory, keywords in keywords_dict.items():
            matches = [word for word in keywords if re.search(r'\b' + word + r'\b', dream_text.lower())]
            if matches:
                if category not in categories_found:
                    categories_found[category] = {}
                categories_found[category][subcategory] = matches
    return categories_found


# [Keep the original page config and CSS styling here...]

# Display the header
st.markdown("""
    <style>
    .header-text {
        font-size: 48px;  /* Increased from 32px */
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-family: 'Arial Black', sans-serif;
        animation: fadeIn 1.5s ease-in-out forwards;
    }
    </style>
    <div class="header-text">DREAM ANALYZER 1.0 (BETA)</div>
""", unsafe_allow_html=True)

# Textarea for user input
user_input = st.text_area("Enter your dream details here:", "", height=150)

# Submit button
if st.button("Analyze Dream"):
    if user_input.strip() == "":
        st.warning("Please enter your dream details before analyzing.")
    else:
        with st.spinner("Analyzing your dream..."):
            # Perform analysis
            sentiment, good_matches, bad_matches = classify_sentiment(user_input)
            categories_found = classify_category(user_input)
            time.sleep(1)  # Simulate processing time

        st.success("Dream analysis complete!")

        # Display sentiment with emoji
        sentiment_emoji = "😊" if sentiment == "Positive" else "😞" if sentiment == "Negative" else "😐"
        st.markdown(
            f"<span style='font-size:18px; font-weight:bold; color:#28a745;'>Sentiment: {sentiment} {sentiment_emoji}</span>",
            unsafe_allow_html=True)

        # Show category results in expanded format
        st.subheader("Dream Categories:")
        for category, subcategories in categories_found.items():
            st.markdown(f"**{category}**")
            for subcat, matches in subcategories.items():
                st.write(f"- {subcat.capitalize()}: {', '.join(matches)}")

        # Add rain effect for positive sentiment
        if sentiment == "Positive":
            rain(emoji="✨", font_size=20, falling_speed=3, animation_length="infinite")

# Footer with logo
st.markdown(
    f"""
    <div class='powered-by'>
        <span>Powered by</span>
        <img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="Algo Craft">
    </div>
    """,
    unsafe_allow_html=True
)
