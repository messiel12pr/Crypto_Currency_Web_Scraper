import time
from flask import Flask, session, flash, redirect, render_template, url_for, request
import coingecko_scraper as scraper
import threading

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

url = "https://www.coingecko.com"
header = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
soup = scraper.initialize_soup(url, header)
coins = []
scraper_running = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/add-coin', methods = ['POST', 'GET'])
def add_coin():
    if request.method == 'POST':
        coin = request.form['coin_name'].strip()
        if coin not in coins and len(coins) != 4:
            coins.append(coin)
            print('Coin succesfully added')
        
        elif len(coins) == 4:
            print("Cannot track more than 4 coins at a time")

        else:
            # TODO find a way to display eror messages to user
            print('Coin was already found in the coin list')
    return render_template("index.html", text_list=coins)

@app.route('/remove-coin', methods = ['POST', 'GET'])
def remove_coin():
    if request.method == 'POST':
        coin = request.form['coin_name'].strip()
        if coin in coins:
            coins.remove(coin)
        
        else:
            # TODO find a way to display eror messages to user
            print('Coin not found')
        print(coins)

    return render_template("index.html")

def scraper_task():
    global scraper_running
    while scraper_running:
        print('Scraper running')
        scraper.scrape_data(soup, coins)
        # This will run every 10 minutes once activated
        time.sleep(600)

@app.route('/run-scraper', methods=['POST', 'GET'])
def run_scraper():
    global scraper_running
    if not scraper_running and len(coins) != 0:
        # Start the scraper in a background thread
        scraper_running = True
        scraper_thread = threading.Thread(target=scraper_task)
        scraper_thread.start()

    else:
        # TODO find a way to display eror messages to user
        print('Add some coins to track first!')

    return render_template("index.html")

@app.route('/stop-scraper', methods=['POST', 'GET'])
def stop_scraper():
    global scraper_running
    scraper_running = False
    print('Stopped scraper')
    return render_template("index.html")

@app.route('/show-graph', methods = ['POST', 'GET'])
def show_graph():
    if request.method == 'POST':
        coin = request.form['coin_name'].strip()
        if coin in coins:
            print('Displaying graph')
            fig = scraper.graph_data(coin)
            return render_template('graph.html', plot=fig.to_html(full_html=False, include_plotlyjs='cdn'))

        else:
            # TODO find a way to display eror messages to user
            print('Error displaying graph: Coin not found')
    
    return render_template("index.html")    

if __name__ == "__main__":
    app.run(debug=True)
