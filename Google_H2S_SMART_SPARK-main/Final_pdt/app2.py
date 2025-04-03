from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from bs4 import BeautifulSoup
import datetime
import requests

# Initialize Flask app
app = Flask(__name__)

# Constant for ESP8266 details
ESP8266_IP = "172.19.192.236"  # Replace with your ESP8266's static IP
ESP8266_PORT = 80  # Default HTTP port

# Configure Generative AI API (Replace with your actual API key)
genai.configure(api_key="AIzaSyC7EvEAU2jL-g92frZ9hjJXd_54s6WLsrM")

# Utility: Read webpage content
def read_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text()
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None

# ESP8266 Communication Route
@app.route("/send", methods=["POST"])
def send_text():
    text = request.form.get("text")
    if text:
        try:
            url = f"http://{ESP8266_IP}:{ESP8266_PORT}/send"
            response = requests.post(url, json={"text": text})
            if response.status_code == 200:
                return "Text sent successfully!"
            else:
                return f"Failed to send text. ESP8266 responded with: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    else:
        return "No text provided!"

# Generative AI Input Processing
def process_input(user_input, language):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"{user_input} Give precise and small answers. Respond in {language}."
    genairesponse = model.generate_content(prompt)
    return genairesponse.text

# Button Press Handler
@app.route("/button", methods=["POST"])
def button_event():
    data = request.get_json()
    if not data or "button" not in data:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    button = data["button"]
    actions = {
        "top": "ESC",
        "bottom": "Play/Pause",
        "left": "F",
        "right": "J",
        "center": "SPACE"
    }

    if button in actions:
        action = actions[button]
        print(f"Button '{button}' mapped to action '{action}'")
        try:
            import pyautogui
            if action == "Play/Pause":
                pyautogui.press("playpause")
            else:
                pyautogui.press(action.lower())
        except ImportError:
            print("pyautogui not installed. Keystroke simulation skipped.")
        return jsonify({"status": "success", "action": action}), 200

    return jsonify({"status": "error", "message": "Unknown button"}), 400

# News Generation Route
@app.route("/generate_news", methods=["GET", "POST"])
def generate_news():
    url = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRE55YXpBU0JXVnVMVWRDS0FBUAE?hl=en-IN&gl=IN&ceid=IN%3Aen"
    text_content = read_webpage(url)
    if text_content:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""{text_content} Concisely summarize and separate the news. DO NOT INCLUDE ADS. Start with 'Today's top headline is:'."""
        genairesponse = model.generate_content(prompt)
        return render_template("indexN3.html", news=genairesponse.text)
    else:
        return "Failed to fetch or generate news."

# Chatbot Route
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        language = request.form.get("language", "en-US")
        response = process_input(user_input, language)
        return jsonify({"message": response})
    return jsonify({"message": "Hello from Flask! How can I assist you?"})

# Multilingual Routes
@app.route("/kannada", methods=["GET", "POST"])
def kannada():
    response = None
    if request.method == "POST":
        user_input = request.form.get("user_input")
        response = process_input(user_input, "kn-IN")
    return render_template("kannada.html", response=response)

@app.route("/english", methods=["GET", "POST"])
def english():
    response = None
    if request.method == "POST":
        user_input = request.form.get("user_input")
        response = process_input(user_input, "en-US")
    return render_template("english.html", response=response)

@app.route("/telugu", methods=["GET", "POST"])
def telugu():
    response = None
    if request.method == "POST":
        user_input = request.form.get("user_input")
        response = process_input(user_input, "te-IN")
    return render_template("telugu.html", response=response)

# General Routes for Static Pages
@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/l")
def learn():
    return render_template("learn.html")

@app.route("/s")
def static_abc():
    return render_template("StaticABC.html")

@app.route("/q")
def quiz_home():
    return render_template("Quizhome.html")

@app.route("/geo")
def geo():
    return render_template("geo.html")

@app.route("/i")
def index():
    return render_template("index.html")

@app.route("/gk")
def gk():
    return render_template("gk.html")

@app.route("/math")
def math():
    return render_template("math.html")

@app.route("/social")
def social():
    return render_template("social.html")

@app.route("/music")
def music():
    return render_template("music.html")

@app.route("/motivation")
def motivation():
    return render_template("Motivation.html")

@app.route("/exam")
def exam():
    return render_template("exam.html")

@app.route("/examp2")
def exam_p2():
    return render_template("examp2.html")

@app.route("/news")
def news():
    return render_template("indexN3.html")

@app.route("/filesummary")
def file_summary():
    return render_template("FileSummary.html")

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)