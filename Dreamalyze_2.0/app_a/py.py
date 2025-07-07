#!/usr/bin/env python3
"""
DeepSeek Dream Analyzer Backend
Real AI integration using DeepSeek model for dream interpretation
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
from datetime import datetime
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class DeepSeekDreamAnalyzer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.loading = False

        # Use a smaller, faster DeepSeek model
        self.model_name = "deepseek-ai/deepseek-coder-1.3b-base"  # Lightweight model

        # Dream categories from your data
        self.categories = {
            "Perception": {
                "colour": ["red", "yellow", "blue", "green", "purple", "orange", "black", "white", "pink", "brown"],
                "hearing": ["music", "voice", "sound", "noise", "melody", "rhythm", "scream", "echo", "whisper",
                            "humming"],
                "smell": ["fragrance", "odor", "perfume", "aroma", "scent", "stink", "smoke", "essence", "stench",
                          "bouquet"],
                "taste": ["sweet", "bitter", "salty", "sour", "spicy", "savory", "tangy", "bland", "umami", "zesty"],
                "touch": ["soft", "rough", "smooth", "sticky", "cold", "warm", "hot", "slippery", "fuzzy", "wet"],
                "vision": ["light", "dark", "bright", "dim", "shiny", "shadow", "colorful", "gloomy", "sparkling",
                           "blurry"],
            },
            "Emotion": {
                "anger": ["rage", "fury", "mad", "irritation", "annoyance", "hatred", "resentment", "wrath",
                          "frustration", "agitation"],
                "happiness": ["joy", "smile", "laugh", "glee", "delight", "pleasure", "bliss", "contentment", "mirth",
                              "cheer"],
                "fear": ["scared", "terror", "panic", "fright", "anxiety", "dread", "nervousness", "phobia", "horror",
                         "unease"],
                "wonder": ["awe", "amazement", "curiosity", "marvel", "fascination", "intrigue", "astonishment",
                           "admiration", "surprise", "interest"],
                "sadness": ["tears", "grief", "sorrow", "loneliness", "melancholy", "heartbreak", "despair", "mourning",
                            "anguish", "regret"],
            },
            "Movement": {
                "falling": ["drop", "collapse", "plunge", "tumble", "descend", "slip", "stumble", "crash", "dive",
                            "topple"],
                "flying": ["soar", "glide", "hover", "float", "ascend", "drift", "takeoff", "pilot", "flap",
                           "airborne"],
                "walking": ["stroll", "march", "stride", "amble", "wander", "hike", "saunter", "trek", "pace", "roam"],
                "running": ["sprint", "dash", "jog", "rush", "hurry", "race", "chase", "gallop", "bolt", "charge"],
            },
            "Characters": {
                "animals": ["dog", "cat", "lion", "tiger", "bear", "rabbit", "snake", "bird", "fish", "elephant"],
                "family": ["mother", "father", "child", "brother", "sister", "parent", "son", "daughter", "grandparent",
                           "cousin"],
                "fantastic beings": ["dragon", "elf", "ghost", "fairy", "wizard", "unicorn", "goblin", "troll",
                                     "vampire", "mermaid"],
            },
            "Natural Elements": {
                "water": ["river", "ocean", "rain", "lake", "stream", "wave", "sea", "pond", "waterfall", "tide"],
                "fire": ["flame", "burn", "ash", "blaze", "inferno", "spark", "ember", "smoke", "torch", "wildfire"],
                "air": ["wind", "breeze", "storm", "gust", "hurricane", "cyclone", "draft", "whirlwind", "current",
                        "airflow"],
                "earth": ["soil", "rock", "sand", "mud", "clay", "pebble", "gravel", "mountain", "hill", "valley"],
            }
        }

    def load_model(self):
        """Load the DeepSeek model"""
        if self.loading or self.model_loaded:
            return

        self.loading = True
        logger.info(f"Loading DeepSeek model: {self.model_name}")

        try:
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir="./models"
            )

            # Add padding token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model with optimizations for CPU/GPU
            logger.info("Loading model...")
            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                cache_dir="./models"
            )

            if device == "cpu":
                self.model = self.model.to(device)

            self.model_loaded = True
            logger.info(f"Model loaded successfully on {device}")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model_loaded = False
        finally:
            self.loading = False

    def analyze_dream(self, dream_text):
        """Analyze dream using DeepSeek model and categories"""
        if not self.model_loaded:
            return {
                "error": "Model not loaded",
                "analysis": "Please load the model first"
            }

        try:
            # First, categorize the dream elements
            detected_elements = self._categorize_dream(dream_text)

            # Create a specialized prompt for dream analysis
            prompt = self._create_dream_prompt(dream_text, detected_elements)

            # Generate AI analysis
            ai_analysis = self._generate_analysis(prompt)

            # Combine categorical analysis with AI insights
            final_analysis = self._combine_analyses(detected_elements, ai_analysis, dream_text)

            return {
                "success": True,
                "analysis": final_analysis,
                "detected_elements": detected_elements,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing dream: {str(e)}")
            return {
                "error": str(e),
                "analysis": "Error occurred during analysis"
            }

    def _categorize_dream(self, dream_text):
        """Categorize dream elements based on predefined categories"""
        text_lower = dream_text.lower()
        detected = {}

        for main_cat, sub_cats in self.categories.items():
            found_in_main = {}
            for sub_cat, words in sub_cats.items():
                matches = [word for word in words if word.lower() in text_lower]
                if matches:
                    found_in_main[sub_cat] = matches

            if found_in_main:
                detected[main_cat] = found_in_main

        return detected

    def _create_dream_prompt(self, dream_text, detected_elements):
        """Create specialized prompt for dream analysis"""
        elements_text = ""
        if detected_elements:
            elements_text = "\n\nDetected symbolic elements:\n"
            for main_cat, sub_cats in detected_elements.items():
                elements_text += f"- {main_cat}: "
                for sub_cat, words in sub_cats.items():
                    elements_text += f"{sub_cat} ({', '.join(words)}); "
                elements_text += "\n"

        prompt = f"""As a dream analyst, provide a psychological interpretation of this dream:

Dream Description: "{dream_text}"
{elements_text}

Please provide a detailed analysis covering:
1. Main themes and symbols
2. Emotional significance  
3. Psychological interpretation
4. Possible life connections
5. Actionable insights

Analysis:"""

        return prompt

    def _generate_analysis(self, prompt):
        """Generate analysis using DeepSeek model"""
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )

            # Move to same device as model
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=300,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the new generated part
            ai_analysis = full_response[len(prompt):].strip()

            return ai_analysis if ai_analysis else "The AI generated an empty response. Please try again."

        except Exception as e:
            logger.error(f"Error in AI generation: {str(e)}")
            return f"AI generation error: {str(e)}"

    def _combine_analyses(self, detected_elements, ai_analysis, dream_text):
        """Combine categorical and AI analyses"""
        analysis = "🌙 DEEPSEEK DREAM ANALYSIS\n"
        analysis += "=" * 50 + "\n\n"

        # Detected elements section
        analysis += "🔍 DETECTED SYMBOLIC ELEMENTS:\n"
        if detected_elements:
            for main_cat, sub_cats in detected_elements.items():
                analysis += f"\n📁 {main_cat.upper()}:\n"
                for sub_cat, words in sub_cats.items():
                    analysis += f"   • {sub_cat.title()}: {', '.join(words)}\n"
        else:
            analysis += "No specific symbolic patterns detected.\n"

        analysis += "\n🤖 AI INTERPRETATION:\n"
        analysis += "-" * 30 + "\n"
        analysis += ai_analysis + "\n"

        # Add quick insights based on detected elements
        analysis += "\n💡 SYMBOLIC INSIGHTS:\n"
        insights = self._get_symbolic_insights(detected_elements)
        for insight in insights:
            analysis += f"• {insight}\n"

        analysis += "\n" + "=" * 50 + "\n"
        analysis += "✨ This analysis combines AI interpretation with symbolic pattern recognition.\n"
        analysis += "Remember: Dreams are highly personal - trust your own intuition about what resonates."

        return analysis

    def _get_symbolic_insights(self, detected_elements):
        """Get quick symbolic insights based on detected elements"""
        insights = []

        if "Movement" in detected_elements:
            if "flying" in detected_elements["Movement"]:
                insights.append("Flying symbolizes freedom, transcendence, or desire to rise above current situations")
            if "falling" in detected_elements["Movement"]:
                insights.append("Falling often represents loss of control, anxiety, or fear of failure")
            if "running" in detected_elements["Movement"]:
                insights.append("Running may indicate urgency, escape, or pursuit of goals")

        if "Emotion" in detected_elements:
            if "fear" in detected_elements["Emotion"]:
                insights.append("Fear elements suggest anxieties that may need addressing in waking life")
            if "happiness" in detected_elements["Emotion"]:
                insights.append("Positive emotions indicate contentment and life satisfaction")

        if "Natural Elements" in detected_elements:
            if "water" in detected_elements["Natural Elements"]:
                insights.append("Water represents emotions, the unconscious mind, and life flow")
            if "fire" in detected_elements["Natural Elements"]:
                insights.append("Fire symbolizes passion, transformation, or destructive/creative energy")

        if "Characters" in detected_elements:
            if "family" in detected_elements["Characters"]:
                insights.append("Family members often represent aspects of yourself or important relationships")
            if "animals" in detected_elements["Characters"]:
                insights.append("Animals typically symbolize instincts, natural desires, or specific traits")

        return insights if insights else ["Your dream contains unique elements requiring personal interpretation"]


# Initialize the analyzer
dream_analyzer = DeepSeekDreamAnalyzer()


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/load_model', methods=['POST'])
def load_model():
    """Load the DeepSeek model"""
    if dream_analyzer.model_loaded:
        return jsonify({
            "success": True,
            "message": "Model already loaded",
            "model_name": dream_analyzer.model_name
        })

    if dream_analyzer.loading:
        return jsonify({
            "success": False,
            "message": "Model is currently loading, please wait..."
        })

    # Load model in background thread
    def load_in_background():
        dream_analyzer.load_model()

    thread = threading.Thread(target=load_in_background)
    thread.start()

    return jsonify({
        "success": True,
        "message": "Model loading started...",
        "model_name": dream_analyzer.model_name
    })


@app.route('/model_status', methods=['GET'])
def model_status():
    """Check model loading status"""
    return jsonify({
        "loaded": dream_analyzer.model_loaded,
        "loading": dream_analyzer.loading,
        "model_name": dream_analyzer.model_name
    })


@app.route('/analyze', methods=['POST'])
def analyze_dream():
    """Analyze a dream"""
    try:
        data = request.get_json()
        dream_text = data.get('dream', '').strip()

        if not dream_text:
            return jsonify({
                "success": False,
                "error": "No dream text provided"
            })

        # Analyze the dream
        result = dream_analyzer.analyze_dream(dream_text)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available dream categories"""
    return jsonify({
        "categories": dream_analyzer.categories,
        "total_categories": len(dream_analyzer.categories)
    })


if __name__ == '__main__':
    print("🌙 DeepSeek Dream Analyzer Backend Starting...")
    print(f"📁 Model will be cached in: ./models/")
    print(f"🔗 Frontend URL: http://localhost:5000")
    print(f"🤖 Model: {dream_analyzer.model_name}")
    print("\n⚡ Starting Flask server...")

    # Create models directory
    os.makedirs("./models", exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)