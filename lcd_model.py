from model import Model
import lcd.drivers as drivers 
from time import sleep

display = drivers.Lcd()

default_stocks = ["AAPL", "GOOG", "META", "TSLA", "MSFT"]
default_stock_index = 0

def scroll_stocks(message: str):
    if message == "next":
        default_stock_index = (default_stock_index + 1) % len(default_stocks)
    elif message == "previous":
        default_stock_index = (default_stock_index - 1) % len(default_stocks)
    else: # Only works for the initial start of the program
        default_stock_index = 0
        
    model = Model(default_stocks[default_stock_index])
    score = model.start()
    score = score[0] if not isinstance(score, int) else score
    
    
    

def process_message(message: str):
    try:
        if message in ["next", "prev"]:
            scroll_stocks(message)
        else:
            display.lcd_display_string("Message Recieved", 1)
            display.lcd_display_string(message, 2)
            
            sleep(3)
            display.lcd_clear()
            
            
            display.lcd_display_string(message, 1)
    except KeyboardInterrupt:
        print("Cleaning up!")
        display.lcd_clear()




diffs = []
for stock in default_stocks:
    model = Model(stock)
    diff = model.start()
    diffs.append([stock, diff[0] if not isinstance(diff, int) else diff])

print(diffs)