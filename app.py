from flask import Flask, session, flash, redirect, render_template, url_for, request
import coingecko_scraper as scraper

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

url = "https://www.coingecko.com"
header = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
coins = []
soup = scraper.initialize_soup(url, header)


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/add-coin', methods = ['POST', 'GET'])
def add_coin():
    if request.method == 'POST':
        coin = request.form['coin_name']
        if coin not in coins:
            coins.append(coin)
        
        print(coins)

    return render_template("index.html")

@app.route('/remove-coin', methods = ['POST', 'GET'])
def remove_coin():
    if request.method == 'POST':
        coin = request.form['coin_name']
        if coin in coins:
            coins.remove(coin)
        
        print(coins)

    return render_template("index.html")

@app.route('/run-scraper', methods = ['POST', 'GET'])
def run_scraper():
    print('Running scraper')
    # TODO Create function in coingecko_scraper to
    # run the scraper until we hit  the Stop Scraper button
    return render_template("index.html")

@app.route('/stop-scraper', methods = ['POST', 'GET'])
def stop_scraper():
    print('Stoped scraper')
    # TODO Create function in coingecko_scraper to
    # stop the scraper 
    return render_template("index.html")

@app.route('/show-graph', methods = ['POST', 'GET'])
def show_graph():
    print('Displaying graph')
    # TODO Create function in to display
    # a matplotlib graph of the coin
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
