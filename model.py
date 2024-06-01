import os  # For interacting with the operating system
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For numerical computations
import matplotlib.pyplot as plt  # For plotting data
from sklearn.preprocessing import MinMaxScaler  # For scaling features
from keras.layers import LSTM, Dense  # For building LSTM model layers
from sklearn.model_selection import TimeSeriesSplit  # For splitting time series data
from keras.models import Sequential, load_model  # For creating and loading models
import yfinance as yf  # For fetching financial data

from i2c_dev import Lcd  # Custom module for LCD control

# Initialize the LCD display
display = Lcd()

# Define the Model class for stock prediction
class Model:
    def __init__(self, stock: str):
        self.__stock = stock  # Store the stock symbol
        self.df = None  # DataFrame to hold stock data
        self.scaler = MinMaxScaler()  # Scaler for feature scaling
        self.lstm = None  # Variable to hold the LSTM model
        self.model_path = f"models/{stock}.keras"  # Path to store the model

    # Fetch historical stock data using yfinance
    def fetch_data(self):
        self.df = yf.Ticker(self.__stock).history(period="10y")  # Fetch 10 years of data
        self.df = pd.DataFrame(self.df)  # Convert to DataFrame
        
        if self.df.size == 0:
            raise ValueError(f"{self.__stock} Not Found!")  # Raise an error if no data is found

    # Plot the initial stock data
    def plot_initial_data(self):
        self.df['Close'].plot()  # Plot the closing prices
        plt.title("Initial Stock Data")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.show()

    # Scale the features for the LSTM model
    def scale_features(self):
        features = ["Open", "High", "Low", "Volume"]  # Features to scale
        feature_transform = self.scaler.fit_transform(self.df[features])  # Scale features
        self.feature_transform = pd.DataFrame(columns=features, data=feature_transform, index=self.df.index)  # Create a DataFrame with the scaled features

    # Split the data into training and testing sets using TimeSeriesSplit
    def split_data(self):
        timesplit = TimeSeriesSplit(n_splits=10)  # Define the number of splits
        for train_index, test_index in timesplit.split(self.feature_transform):
            X_train = self.feature_transform[:len(train_index)]  # Training features
            X_test = self.feature_transform[len(train_index):(len(train_index)+len(test_index))]  # Testing features
            y_train = self.df["Close"][:len(train_index)].values.ravel()  # Training target
            y_test = self.df["Close"][len(train_index):(len(train_index)+len(test_index))].values.ravel()  # Testing target
        return X_train, X_test, y_train, y_test

    # Prepare the data for the LSTM model
    def prepare_data_for_lstm(self, X_train, X_test):
        trainX = np.array(X_train)
        testX = np.array(X_test)
        X_train = trainX.reshape(X_train.shape[0], 1, trainX.shape[1])  # Reshape for LSTM
        X_test = testX.reshape(X_test.shape[0], 1, testX.shape[1])  # Reshape for LSTM
        return X_train, X_test

    # Build and train the LSTM model
    def build_and_train_lstm(self, X_train, y_train):
        self.lstm = Sequential()  # Initialize the Sequential model
        self.lstm.add(LSTM(32, input_shape=(1, X_train.shape[2]), activation='relu', return_sequences=False))  # Add LSTM layer
        self.lstm.add(Dense(1))  # Add output layer
        self.lstm.compile(loss='mean_squared_error', optimizer='adam')  # Compile the model
        history = self.lstm.fit(X_train, y_train, epochs=50, batch_size=8, verbose=1, shuffle=False)  # Train the model
        return history

    # Plot the true and predicted values
    def plot_predictions(self, y_pred, y_test):
        plt.plot(y_test, label='True Value')  # Plot true values
        plt.plot(y_pred, label='LSTM Value')  # Plot predicted values
        plt.title("Prediction by LSTM")
        plt.xlabel('Time Scale')
        plt.ylabel('Scaled USD')
        plt.legend()
        plt.show()

    # Score the stock predictions
    def score_stock(self, y_train, X_test, y_test):
        y_pred = self.lstm.predict(X_test)  # Predict values using the LSTM model
        # self.plot_predictions(y_pred, y_test)  # Optionally plot the predictions

        earliest_actual = y_train[:30]  # First 30 actual values for comparison
        latest_actual = y_test[-30:]  # Last 30 actual values
        latest_pred = y_pred[-30:]  # Last 30 predicted values
        
        total_diff = 0
        for i in range(30):
            diff = abs((latest_pred[i] - latest_actual[i]) / latest_actual[i])  # Calculate absolute percentage difference
            total_diff += diff
        
        avg_diff = total_diff / 30  # Calculate average difference
        
        if sum(earliest_actual) - sum(latest_actual) > 0:  # If there's a significant decrease, adjust the score
            avg_diff += .35
        
        score = 100 - min(avg_diff * 100, 100)  # Calculate score
        
        print(f"Score: {score} / 100")  # Print the score
        
        return score

    # Start the model training and evaluation process
    def start(self):
        self.fetch_data()  # Fetch the data
        self.scale_features()  # Scale the features
        X_train, X_test, y_train, y_test = self.split_data()  # Split the data
        X_train, X_test = self.prepare_data_for_lstm(X_train, X_test)  # Prepare the data for LSTM
        
        if os.path.exists(self.model_path):  # Check if the model already exists
            self.lstm = load_model(self.model_path)  # Load the existing model
            print(f"{self.__stock}'s model loaded from the 'res' folder.")
        else:
            display.lcd_clear()  # Clear the LCD display
            display.lcd_display_string("Loading Model", 1)  # Display loading message
            display.lcd_display_string(f"{self.__stock}", 2)  # Display stock symbol

            self.build_and_train_lstm(X_train, y_train)  # Build and train the model
            self.lstm.save(self.model_path)  # Save the trained model
            print(f"{self.__stock}'s model saved to the 'res' folder.")

        return self.score_stock(y_train, X_test, y_test)  # Score the model and return the score
