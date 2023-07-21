from flask import Flask, render_template, url_for
import coingecko_scraper as scraper

app = Flask(__name__)

url = "https://www.coingecko.com"
header = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
coins = ["Bitcoin", "Ethereum", "Tether", "Cardano", "Solana"]
soup = scraper.initialize_soup(url, header)

@app.route("/")
def index():
    print(scraper.csv_to_string())
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
