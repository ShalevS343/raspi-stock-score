from model import Model

def main():
    default_stocks = ['NIO', 'AAPL', 'AMZN', 'GOOGL', 'TSLA', 'META', 'NVDA', 'WMT', 'XOM', 'UNH', 'CVS', 'MCK', 'CVX', 'COST']
    
    diffs = []
    for stock in default_stocks:
        model = Model(stock)
        diffs.append([stock, model.start()[0]])
    
    print(diffs)
        
if __name__ == "__main__":
    main()