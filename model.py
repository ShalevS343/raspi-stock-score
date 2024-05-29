import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.layers import LSTM, Dense
from sklearn.model_selection import TimeSeriesSplit
from keras.models import Sequential, load_model
import yfinance as yf

class Model:
    def __init__(self, stock: str):
        self.__stock = stock
        self.df = None
        self.scaler = MinMaxScaler()
        self.lstm = None
        self.model_path = f"models/{stock}"  # Path to store the model


    def fetch_data(self):
        self.df = yf.Ticker(self.__stock).history(period="10y")
        self.df = pd.DataFrame(self.df)
        
        if self.df.size == 0:
            raise Exception(f"Invalid Stock Ticker {self.__stock}")

    def plot_initial_data(self):
        self.df['Close'].plot()
        plt.title("Initial Stock Data")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.show()

    def scale_features(self):
        features = ["Open", "High", "Low", "Volume"]
        feature_transform = self.scaler.fit_transform(self.df[features])
        self.feature_transform = pd.DataFrame(columns=features, data=feature_transform, index=self.df.index)

    def split_data(self):
        timesplit = TimeSeriesSplit(n_splits=10)
        for train_index, test_index in timesplit.split(self.feature_transform):
            X_train, X_test = self.feature_transform[:len(train_index)], self.feature_transform[len(train_index):(len(train_index)+len(test_index))]
            y_train, y_test = self.df["Close"][:len(train_index)].values.ravel(), self.df["Close"][len(train_index):(len(train_index)+len(test_index))].values.ravel()
        return X_train, X_test, y_train, y_test

    def prepare_data_for_lstm(self, X_train, X_test):
        trainX = np.array(X_train)
        testX = np.array(X_test)
        X_train = trainX.reshape(X_train.shape[0], 1, trainX.shape[1])
        X_test = testX.reshape(X_test.shape[0], 1, testX.shape[1])
        return X_train, X_test

    def build_and_train_lstm(self, X_train, y_train):
        self.lstm = Sequential()
        self.lstm.add(LSTM(32, input_shape=(1, X_train.shape[2]), activation='relu', return_sequences=False))
        self.lstm.add(Dense(1))
        self.lstm.compile(loss='mean_squared_error', optimizer='adam')
        history = self.lstm.fit(X_train, y_train, epochs=50, batch_size=8, verbose=1, shuffle=False)
        return history

    def plot_predictions(self, y_pred, y_test):
        plt.plot(y_test, label='True Value')
        plt.plot(y_pred, label='LSTM Value')
        plt.title("Prediction by LSTM")
        plt.xlabel('Time Scale')
        plt.ylabel('Scaled USD')
        plt.legend()
        plt.show()

    def score_stock(self, y_train, X_test, y_test):
        y_pred = self.lstm.predict(X_test)
        # self.plot_predictions(y_pred, y_test)

        earliest_actual = y_train[:30]
        # Compare predictions with actual values
        latest_actual = y_test[-30:]
        latest_pred = y_pred[-30:]
        
        total_diff = 0
        for i in range(30):
            diff = abs((latest_pred[i] - latest_actual[i]) / latest_actual[i])
            total_diff += diff
        
        avg_diff = total_diff / 30
        
        if sum(earliest_actual) - sum(latest_actual) > 0:
            avg_diff += .35
        
        # Penalize larger differences
        score = 100 - min(avg_diff * 100, 100)
        
        print(f"Score: {score} / 100")
        
        return score


    def start(self):
        self.fetch_data()
        self.scale_features()
        X_train, X_test, y_train, y_test = self.split_data()
        X_train, X_test = self.prepare_data_for_lstm(X_train, X_test)
        
        if os.path.exists(self.model_path):
            # If the model is already downloaded, load it
            self.lstm = load_model(self.model_path)
            print(f"{self.__stock}'s model loaded from the 'res' folder.")
        else:
            # If the model is not downloaded, start the LSTM process
            self.build_and_train_lstm(X_train, y_train)
            self.lstm.save(self.model_path)
            print(f"{self.__stock}'s model saved to the 'res' folder.")

        # Score the model
        return self.score_stock(y_train, X_test, y_test)
