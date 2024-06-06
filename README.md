# Raspberry Pi Stock Score
## Summery
The project involves developing an embedded system using a Raspberry Pi 4 to predict and rank stock prices utilizing an LSTM model. The system features a Bluetooth server for user connectivity, an LCD screen for displaying stock information, and buttons for user interaction. Upon receiving a stock query via Bluetooth, the system processes the request using the LSTM model, either training on new stock data or retrieving previously learned data. Results are displayed on the LCD screen. This project integrates hardware communication through I2C and Bluetooth to create an interactive and user-friendly stock analysis tool.

## Run
In order to run setup bluetooth according to the following video
[Bluetooth Setup Guide for Raspberry Pi](https://www.youtube.com/watch?v=DmtJBc229Rg)

After setting up according to the video open the terminal and run the server via:
`sudo python3 rfcomm-server.py`

After that connect to the RaspberryPi from a [Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal&hl=en_NZ#) app in your phone

Follow the README in each of the following repositories
[LCD - The Raspberry Pi Guy](https://github.com/the-raspberry-pi-guy/lcd)
[Pybluez](https://github.com/pybluez/pybluez) (This one is already used if u follow the video about bluetooth in Raspberry Pi above so if you did it there is no reason to do it twice).

