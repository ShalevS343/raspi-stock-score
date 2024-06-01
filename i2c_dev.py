from smbus import SMBus
from RPi.GPIO import RPI_REVISION
from time import sleep
from re import findall, match
from subprocess import check_output
from os.path import exists

# Determine the I2C bus number based on the Raspberry Pi version
# Old and new versions of the RPi have swapped the two I2C buses
BUS_NUMBER = 0 if RPI_REVISION == 1 else 1

# LCD command definitions
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# Flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00
SESSION_STATE_BACKLIGHT = ''

# Bit masks for controlling the LCD
En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit

class I2CDevice:
    def __init__(self, addr=None, addr_default=None, bus=BUS_NUMBER):
        if not addr:
            # Try to autodetect the I2C address, otherwise use the default if provided
            try:
                self.addr = int('0x{}'.format(
                    findall("[0-9a-z]{2}(?!:)", check_output(['/usr/sbin/i2cdetect', '-y', str(BUS_NUMBER)]).decode())[0]), base=16) \
                    if exists('/usr/sbin/i2cdetect') else addr_default
            except:
                self.addr = addr_default
        else:
            self.addr = addr
        self.bus = SMBus(bus)  # Initialize the I2C bus

    # Write a single command to the device
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

    # Write a command with an argument to the device
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

    # Write a block of data to the device
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

    # Read a single byte from the device
    def read(self):
        return self.bus.read_byte(self.addr)

    # Read a byte of data from a specific command register
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

    # Read a block of data from the device
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)


class Lcd:
    def __init__(self, addr=None):
        self.addr = addr
        self.lcd = I2CDevice(addr=self.addr, addr_default=0x27)  # Default I2C address is 0x27
        # Initialize the LCD display
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)
        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)

    # Pulse the enable bit to latch commands
    def lcd_strobe(self, data):
        if SESSION_STATE_BACKLIGHT == 0:
            LCD = LCD_NOBACKLIGHT
        else:
            LCD = LCD_BACKLIGHT
        self.lcd.write_cmd(data | En | LCD)
        sleep(.0005)
        self.lcd.write_cmd(((data & ~En) | LCD))
        sleep(.0001)

    # Write four bits of data to the LCD
    def lcd_write_four_bits(self, data):
        if SESSION_STATE_BACKLIGHT == 0:
            LCD = LCD_NOBACKLIGHT
        else:
            LCD = LCD_BACKLIGHT
        self.lcd.write_cmd(data | LCD)
        self.lcd_strobe(data)

    # Write a command to the LCD
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    # Display a string on the LCD
    def lcd_display_string(self, string, line):
        # Set the cursor to the beginning of the specified line
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)
        # Write each character of the string
        for char in string:
            self.lcd_write(ord(char), Rs)

    # Display an extended string on the LCD
    def lcd_display_extended_string(self, string, line):
        # Set the cursor to the beginning of the specified line
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)
        # Process the string for extended characters
        while string:
            result = match(r'\{0[xX][0-9a-fA-F]{2}\}', string)
            if result:
                self.lcd_write(int(result.group(0)[1:-1], 16), Rs)
                string = string[6:]
            else:
                self.lcd_write(ord(string[0]), Rs)
                string = string[1:]

    # Clear the LCD display and reset the cursor to the home position
    def lcd_clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)

    # Control the LCD backlight (on/off)
    def lcd_backlight(self, state):
        global SESSION_STATE_BACKLIGHT
        if state == 1:
            self.lcd.write_cmd(LCD_BACKLIGHT)
        elif state == 0:
            self.lcd.write_cmd(LCD_NOBACKLIGHT)

        if state == 1 or state == 0:  # Save backlight settings
            SESSION_STATE_BACKLIGHT = state

class CustomCharacters:
    def __init__(self, lcd):
        self.lcd = lcd
        # Data for custom characters (each character is 5x8 pixels)
        self.char_1_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_2_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_3_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_4_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_5_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_6_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_7_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        self.char_8_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]

    # Load custom character data into CG RAM for later use
    def load_custom_characters_data(self):
        self.chars_list = [self.char_1_data, self.char_2_data, self.char_3_data,
                           self.char_4_data, self.char_5_data, self.char_6_data,
                           self.char_7_data, self.char_8_data]

        # Commands to load character address to CG RAM starting from base addresses
        char_load_cmds = [0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78]
        for char_num in range(8):
            # Command to start loading data into CG RAM
            self.lcd.lcd_write(char_load_cmds[char_num])
            for line_num in range(8):
                line = self.chars_list[char_num][line_num]
                binary_str_cmd = "0b000{0}".format(line)
                self.lcd.lcd_write(int(binary_str_cmd, 2), Rs)
