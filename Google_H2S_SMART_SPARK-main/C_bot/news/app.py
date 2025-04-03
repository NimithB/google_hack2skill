from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import google.generativeai as genai
import datetime
import requests

today = datetime.date.today()


genai.configure(api_key="AIzaSyC7EvEAU2jL-g92frZ9hjJXd_54s6WLsrM")
app = Flask(__name__)

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


@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/generate_news", methods=["GET","POST"])
def generate_news():
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""{text_content} Concise this and seperate the news.DO NOT INCLUDE ADS. IF YOU FIND ANY REMOVE THEM. And while starting the news say 'Today's top headline is'"""
    genairesponse = model.generate_content(prompt)

    response = f"{genairesponse.text}"
    return render_template("index.html", news=response)

if __name__ == "__main__":
    app.run(debug=True)