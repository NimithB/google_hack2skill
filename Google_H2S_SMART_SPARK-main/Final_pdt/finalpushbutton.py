from flask import Flask, render_template, request, jsonify, redirect, url_for
import google.generativeai as genai
import requests
import threading
from pynput.keyboard  import Controller,Key 
from bs4 import BeautifulSoup
# Initialize Flask application
app = Flask(__name__)

# Initialize the Keyboard Controller
keyboard = Controller()

# Global variable to store button press data
button_data = {"button": "No button pressed"}

# Constant IP address of the ESP8266
ESP8266_IP = "172.19.192.236"  # Replace with your ESP8266's static IP
ESP8266_PORT = 80  # Default HTTP port

# Configure Generative AI API (Replace with your actual API key)
genai.configure(api_key="AIzaSyC7EvEAU2jL-g92frZ9hjJXd_54s6WLsrM")  # Replace with your actual API key


@app.route("/send", methods=["POST"])
def send_text():
    # Get the texWQt from the HTML form
    text = request.form.get("text")

    if text:
        try:                                                                                                                
            # Send the text to the ESP8266
            url = f"http://{ESP8266_IP}:{ESP8266_PORT}/send"
            response = requests.post(url, json={"text": text})

            if response.status_code == 200:
                return f"sent"
            else:
                return f"Failed to send text. ESP8266 responded with: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    else:
        return "No text provided!"

 
# Route to receive button press data from ESP8266
@app.route('/esp-data', methods=['POST'])
def receive_data():
    global button_data
    if request.is_json:
        button_data = request.get_json()
        print("Button press received:", button_data)
        # Trigger keyboard operation based on the button press
        handle_keyboard_action(button_data['button'])
        return jsonify({"message": "Button data received successfully"}), 200
    return jsonify({"error": "Invalid data format"}), 400


# Function to map button press to keyboard action
def handle_keyboard_action(button_name):
    if button_name == "TOP":
        keyboard.press('e')
        keyboard.release('e')
        print("Pressed ESC")
    elif button_name == "BOTTOM":
        keyboard.press('h')
        keyboard.release('h')
        print("Pressed H")
    elif button_name == "LEFT":
        keyboard.press('f')
        keyboard.release('f')
        print("Pressed F")
    elif button_name == "RIGHT":
        keyboard.press('j')
        keyboard.release('j')
        print("Pressed J")
    elif button_name == "CENTER":
        keyboard.press(' ')
        keyboard.release(' ')
        print("Pressed Space")

# Routes for the web app
@app.route('/')
def home():
    return render_template('index2.html')


@app.route('/l')
def l():
    return render_template('learn.html')


@app.route('/s')
def s():
    return render_template('StaticABC.html')


@app.route('/q')
def q():
    return render_template('Quizhome.html')


@app.route('/geo')
def geo():
    return render_template('geo.html')


@app.route('/i')
def i():
    return render_template('index.html')


@app.route('/gk')
def gk():
    return render_template('gk.html')


@app.route('/math')
def math():
    return render_template('math.html')


@app.route('/social')
def social():
    return render_template('social.html')


@app.route('/music')
def music():
    return render_template('music.html')


@app.route('/motivation')
def motivation():
    return render_template('Motivation.html')


@app.route('/exam')
def exam():
    return render_template('exam.html')


@app.route('/examp2')
def examp2():
    return render_template('examp2.html')


@app.route('/news')
def news():
    return render_template('indexN3.html')

@app.route("/generate_news", methods=["GET","POST"])
def generate_news():
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""{text_content} Concise this and seperate the news.DO NOT INCLUDE ADS. IF YOU FIND ANY REMOVE THEM. And while starting the news say 'Today's top headline is'"""
    genairesponse = model.generate_content(prompt)
    response = f"{genairesponse.text}"
    return render_template("indexN3.html", news=response)

def read_webpage(url):
  try:
    response = requests.get(url)

    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")
      return soup.get_text()
    else:
      print(f"Failed to retrieve the page. Status code: {response.status_code}")
      return None  # Indicate failure by returning None

  except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the webpage: {e}")
    return None  # Handle network or other request exceptions

# Example usage
url = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRE55YXpBU0JXVnVMVWRDS0FBUAE?hl=en-IN&gl=IN&ceid=IN%3Aen"
text_content = read_webpage(url)

@app.route('/filesummary')
def filesummary():
    return render_template('FileSummary.html')


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        language = request.form.get('language', 'en-US')
        response = process_input(user_input, language)
        return jsonify({"message": response})
    return jsonify({"message": "Hello from Flask! How can I assist you?"})


@app.route('/kannada', methods=['GET', 'POST'])
def kannada():
    response = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = process_input(user_input, 'kn-IN')
    return render_template('kannada.html', response=response)


@app.route('/english', methods=['GET', 'POST'])
def english():
    response = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = process_input(user_input, 'en-US')
    return render_template('english.html', response=response)


@app.route('/telugu', methods=['GET', 'POST'])
def telugu():
    response = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = process_input(user_input, 'te-IN')
    return render_template('telugu.html', response=response)


# Function to process input using Generative AI
def process_input(user_input, language):
    model = genai.GenerativeModel(f"gemini-1.5-flash")
    prompt = f"{user_input} Give precise and small answers. Give the answer in {language}."
    genairesponse = model.generate_content(prompt)
    return genairesponse.text


# Running the Flask app
if __name__ == '__main__':
    # Start the server in a separate thread to handle real-time button presses
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)).start()
