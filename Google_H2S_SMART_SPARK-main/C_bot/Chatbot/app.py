from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="apikey")  # Replace with your actual API key

def process_input(user_input, language):
    model = genai.GenerativeModel(f"gemini-1.5-flash")
    prompt = f"{user_input} Give precise and small answers. Give the answer in {language}."
    genairesponse = model.generate_content(prompt)
    return genairesponse.text

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)