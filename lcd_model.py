from model import Model  # Import the Model class from model module
from i2c_dev import Lcd  # Import the Lcd class from i2c_dev module
from time import sleep  # Import sleep function for delays
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
prev_button = 17
start_button = 27
next_button = 22

GPIO.setup(prev_button, GPIO.IN)
GPIO.setup(start_button, GPIO.IN)
GPIO.setup(next_button, GPIO.IN)

# Initialize the LCD display
display = Lcd()

# Define default stocks to scroll through
default_stocks = ["AAPL", "GOOG", "META", "TSLA", "MSFT"]
default_stock_index = 0  # Index to keep track of the current stock

current_stock = default_stocks[0]

# Function to scroll through stocks based on the message received
def scroll_stocks(message: str):
    global default_stock_index, current_stock

    # Update the default_stock_index based on the message
    if message == "next":
        default_stock_index = (default_stock_index + 1) % len(default_stocks)  # Go to the next stock
    elif message == "prev":
        default_stock_index = (default_stock_index - 1) % len(default_stocks)  # Go to the previous stock
    current_stock = default_stocks[default_stock_index]  # Get the current stock

def confirm_stock():
	global current_stock
	start_model(current_stock)

# Function to initialize and start the model for a given stock
def start_model(stock: str) -> None:
    try:
        model = Model(stock)  # Create a Model instance for the given stock
        score = model.start()  # Start the model and get the score
        score = score[0] if not isinstance(score, int) else score  # Handle score format
        display.lcd_clear()  # Clear the LCD display
        display.lcd_display_string(stock, 1)  # Display the stock symbol on the first line
        display.lcd_display_string(str(score), 2)  # Display the score on the second line
    except ValueError:  # Handle the case where the stock is not found
        display.lcd_clear()  # Clear the LCD display
        display.lcd_display_string(stock, 1)  # Display the stock symbol on the first line
        display.lcd_display_string("Not Found!", 2)  # Display "Not Found!" on the second line

# Function to process incoming messages and update the display accordingly
def process_message(message: str):
    global current_stock
    try:
        if message in ["next", "prev"]:  # Check if the message is to scroll stocks
            scroll_stocks(message)  # Scroll through the stocks
        elif message == "start":
            confirm_stock()
        elif message != "init_start":
            current_stock = message.upper()  # Convert the message to uppercase for the stock symbol
        if message != "start":
            display.lcd_clear()
            display.lcd_display_string(current_stock, 1)
    except KeyboardInterrupt:  # Handle the KeyboardInterrupt to clean up
        print("Cleaning up!")
        display.lcd_clear()  # Clear the LCD display
