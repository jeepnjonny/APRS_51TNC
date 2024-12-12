import serial
import time
import argparse
import os
import sys

##########
#
# version 0.2
#
##########

class x1c3:
    def __init__(self):
        self.raw = ''       # the raw config string
        self.config = {}    # the parsed configuration dictionary
        self.version = ''   # the hardware/firmware version
        self.voltage = ''   # the battery voltage
        self.port = ''      # the serial port to use
        self.file = ''      # the file to use
        self.parsed = False # has the raw already been parsed?
        self.debugFlag = False


########## Utility routines
    def debug(self, message):
        if self.debugFlag: print(message)

    def setPort(self,name):
        # set the port name
        self.port = name
        return True

    def getPort(self):
        return self.port

    def setFile(self,name):
        # set the file name
        self.file = name
        return True

    def getFile(self):
        return self.file

    def hasConfig(self):
        # return true if the config dictionary has contents
        #if debug: print("hasConfig=", str(bool(self.config)))  #debug print
        return bool(len(self.raw) > 0)

    def printRaw(self):
        print(self.raw)
        return

    def printConfig(self):
        self.debug("PrintConfig...")  #debug print
        #if debug: print("Values: ", self.config)  #debug print
        self.menuHeader()
        for k, v in self.config.items():
            print(k,'=',v)
        # wait for the user before continuing
        print("--------------------------------")
        input("Continue?")

        self.debug("Exit printConfig")   #debug print
        return True

    def encodeHex(self,param,length, pad=b'\xff'):
        # end the passed in string with 0x00 and pad with 0xff
        mystr = self.config[param]
        bytestring = bytes(mystr,'utf-8')
        if len(mystr) < length: bytestring+=b'\x00'
        for x in range(length - len(bytestring)):
            bytestring += pad
        return bytestring

    def intToHex(self,param,bytes=1):
        # Convert the integer to a hexadecimal string, with the specified number of bytes
        hex_str = self.config[param].to_bytes(bytes, 'big')
        return hex_str

########## File routines
    def readFile(self):
        # read the config string from the file in to self.raw
        print("Reading file...")
        try:
            with open(self.file, "rb") as f:
                self.raw = f.read()
                return True
        except Exception as e:
            print("An error occurred:", e)
        return False

    def writeFile(self):
        # write the raw config string from the self.raw to the file
        try:
            with open(self.file, "wb") as f:
                f.write(self.raw)
            return True
        except Exception as e:
            print("An error occurred:", e)
        return False



########## Menu tools
    def menuHeader(self):
        os.system('clear')
        print("--------------------------------")
        print("X1C3 Configuration Tool - KG7KMV")
        print("")
        print("Device FW Version:", self.version)
        print("   Device Voltage:", self.voltage)
        print("    Config loaded:", self.hasConfig())
        print("--------------------------------")

    def printEnum(self,param,options=['Disable','Enable']):
        num = int(self.config[param])
        return options[num]

    def inputChar(self,param,length):
        # ask the user for free form input with character limitation
        prompt = param + " (<="+str(length)+" characters):"
        # keep asking for user input until they have the right input
        while True:
            response = input(prompt).upper()
            if len(response) <= length: break

        self.config[param] = response
        return response

    def toggleVal(self,param):
        # toggle a binary entry
        value = int(bool(self.config[param]) ^ True)
        self.config[param] = value
        return value

    def inputNums(self,param,length):
        # ask the user for free form input with limitation
        prompt = param + " (<="+str(length)+"):"
        # keep asking for user input until they have the right input
        while True:
            response = int(input(prompt))
            if response <= length: break

        self.config[param] = response
        return response

    def inputMenu(self,param,prompt='',options=['Disable','Enable'],quit=False):
        #print the header, options, and a prompt. Return a number string with the selection
        if prompt == '': prompt = param+":"   # if no prompt is given, use the dictionary name as the prompt
        self.menuHeader()
        # print out all the options with an enumerator
        for i in range(len(options)):
            print(i,'-',options[i],' ')
        if quit: print("q - Exit")
        print("--------------------------------")
        # ask for the user input
        response = input(prompt)
        # this allows multiuse: for a general menu and a menu for a dictionary item
        if param != '' and response !='' : self.config[param] = response
        return response

########## Menus
    def editMenu(self):
        # create a user menu to run the program
        while True:
            response = self.inputMenu('',"Selection:",['Setup','Beacon','Bluetooth','Fixed','WiFi','Digpeater','Audio','RF Module','X1C5'],True)
            if response == '0': self.menu_setup()
            elif response == '1': self.menu_beacon()
            elif response == '2': self.menu_bluetooth()
            elif response == '3': self.menu_fixed()
            elif response == '4': self.menu_wifi()
            elif response == '5': self.menu_digi()
            elif response == '6': self.menu_audio()
            elif response == '7': self.menu_rfmodule()
            elif response == '8': self.menu_x1c5()
            else: break

    def menu_setup(self):
        while True:
            response = self.inputMenu('',"Selection:",
                ['   Callsign: '+self.config['CALLSIGN'],
                '       SSID: '+str(self.config['SSID']),
                '  Site Type: '+self.printEnum('Site Type',['Fixed','Mobile','Weather']),
                '        GPS: '+self.printEnum('GPS Enable'),
                '     Icon 1: '+self.config['Icon 1'],
                '     Icon 2: '+self.config['Icon 2'],
                'Icon 2 Time: '+str(self.config['Icon 2 Time'])],
                True)
            if response == '0': self.inputChar('CALLSIGN',7)
            elif response == '1': self.inputMenu('SSID','',['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15'])
            elif response == '2': self.inputMenu('Site Type','',['Fixed','Mobile','Weather'])
            elif response == '3': self.toggleVal('GPS Enable')
            elif response == '4': self.inputChar('Icon 1',2)
            elif response == '5': self.inputChar('Icon 2',2)
            elif response == '6': self.inputNums('Icon 2 Time',999)
            else: break

    def menu_beacon(self):
        while True:
            response = self.inputMenu('',"Selection:",
            ['    Smart Beacon: '+self.printEnum('Smart',['OFF','1','2','3','4','5']),
            '   Manual Enable: '+self.printEnum('Manual Enable'),
            '        GPS Save: '+self.printEnum('GPS Save'),
            '    Queue Enable: '+self.printEnum('Queue Enable'),
            '      Queue Time: '+str(self.config['Queue Time']),
            '     Time Enable: '+self.printEnum('Time Enable'),
            '            Time: '+str(self.config['Time Value']),
            '    MIC-E Enable: '+self.printEnum('MIC-E Enable'),
            '      MIC-E Code: '+self.printEnum('MIC-E Code',['Off Duty','En Route','In Service','Returning','Committed','Special','Priority','Emergency']),
            '         Message: '+self.config['Message'],
            '    Add Mileage: '+self.printEnum('Mileage Enable'),
            '   Add Pressure: '+self.printEnum('Pressure Enable'),
            '    Add Voltage: '+self.printEnum('Voltage Enable'),
            'Add Temperature: '+self.printEnum('Temperature Enable'),
            ' Add Satellites: '+self.printEnum('Satellite Enable'),
            '   Add Odometer: '+self.printEnum('Odometer Enable')],
            True)
            if response == '0': self.inputMenu('Smart','',['OFF','1','2','3','4','5'])
            elif response == '1': self.toggleVal('Manual Enable')
            elif response == '2': self.toggleVal('GPS Save')
            elif response == '3': self.toggleVal('Queue Enable')
            elif response == '4': self.inputNums('Queue Time',9999)
            elif response == '5': self.toggleVal('Time Enable')
            elif response == '6': self.inputNums('Time Value',9999)
            elif response == '7': self.toggleVal('MIC-E Enable')
            elif response == '8': self.inputMenu('MIC-E Code','',['Off Duty','En Route','In Service','Returning','Committed','Special','Priority','Emergency'])
            elif response == '9': self.inputChar('Message',60)
            elif response == '10': self.toggleVal('Mileage Enable')
            elif response == '11': self.toggleVal('Pressure Enable')
            elif response == '12': self.toggleVal('Voltage Enable')
            elif response == '13': self.toggleVal('Temperature Enable')
            elif response == '14': self.toggleVal('Satellite Enable')
            elif response == '15': self.toggleVal('Odometer Enable')
            else: break

    def menu_bluetooth(self):
        while True:
            response = self.inputMenu('',"Selection:",
            [' BT Out 1: '+self.printEnum('BT Out 1',['Off','KISS hex','UI','GPWPL','KISS ascii']),
            ' BT Out 2: '+self.printEnum('BT Out 2',['Off','GPS','Rotator']),
            'BT Enable: '+self.printEnum('BT Enable')],
            True)
            if response == '0': self.inputMenu('BT Out 1','',['Off','KISS hex','UI','GPWPL','KISS ascii'])
            elif response == '1': self.inputMenu('BT Out 2','',['Off','GPS','Rotator'])
            elif response == '2': self.toggleVal('BT Enable')
            else: break

    def menu_fixed(self):
        while True:
            response = self.inputMenu('',"Selection:",
            [' Latitude: '+str(self.config['Latitude']),
            'Longitude: '+str(self.config['Longitude']),
            ' Altitude: '+str(self.config['Altitude'])],
            True)
            if response == '0': self.inputChar('Latitude',8)
            elif response == '1': self.inputChar('Longitude',8)
            elif response == '2': self.inputNums('Altitude',9999)
            else: break

    def menu_digi(self):
        while True:
            response = self.inputMenu('',"Selection:",
            ['Digi 1 Enable: '+self.printEnum('DIGI 1 Enable'),
            '  Digi 1 PATH: '+self.config['DIGI 1'],
            'Digi 2 Enable: '+self.printEnum('DIGI 2 Enable'),
            '  Digi 2 PATH: '+self.config['DIGI 2'],
            '   Digi Delay: '+str(self.config['DIGI Delay']),
            ' Digi Channel: '+self.printEnum('DIGI Channel',['CH A','CH B','CH A+B','Bluetooth'])],
            True)
            if response == '0': self.toggleVal('DIGI 1 Enable')
            elif response == '1': self.inputChar('DIGI 1',6)
            elif response == '2': self.toggleVal('DIGI 2 Enable')
            elif response == '3': self.inputChar('DIGI 2',6)
            elif response == '4': self.inputMenu('DIGI Delay','',['0s','1s','2s','3s','4s','5s'])
            elif response == '5': self.inputMenu('DIGI Channel','',['CH A','CH B','CH A+B','Bluetooth'])
            else: break

    def menu_wifi(self):
        selection = ''
        while True:
            response = self.inputMenu('',"Selection:",
            ['    WiFI SSID: '+str(self.config['Wifi Name']),
            'WiFI Password: '+str(self.config['Wifi Code']),
            '  WiFi Enable: '+self.printEnum('Wifi Enable'),
            '   IP Address: '+str(self.config['IP Address']),
            '      IP Port: '+str(self.config['IP Port']),
            '  IP Protocol: '+self.printEnum('IP Protocol',['UDP','TCP'])],
            True)
            if response == '0': self.inputChar('Wifi Name',16)
            elif response == '1': self.inputChar('Wifi Code',16)
            elif response == '2': self.toggleVal('Wifi Enable')
            elif response == '3': self.inputChar('IP Address',31)
            elif response == '4': self.inputChar('IP Port',6)
            elif response == '5': self.inputMenu('IP Protocol','',['TCP','UDP'])
            else: break

    def menu_audio(self):
        while True:
            response = self.inputMenu('',"Selection:",
            ['Tx Volume: '+self.printEnum('Volume TX',['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB']),
            'Rx Volume: '+self.printEnum('Volume RX',['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB']),
            '  Tx Beep: '+self.printEnum('Beep TX'),
            '  Rx Beep: '+self.printEnum('Beep RX')],
            True)
            if response == '0': self.inputMenu('Volume TX','',['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB'])
            elif response == '1': self.inputMenu('Volume RX','',['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB'])
            elif response == '2': self.toggleVal('Beep TX')
            elif response == '3': self.toggleVal('Beep RX')
            else: break

    def menu_rfmodule(self):
        while True:
            response = self.inputMenu('',"Selection:",
            ['      Power: '+self.printEnum('Module Power',['Off','On','Tx Only','Rx Only']),
            'Frequency 1: '+str(self.config['Frequency 1']),
            'Frequency 2: '+str(self.config['Frequency 2']),
            '     Volume: '+str(self.config['Module Volume']),
            '   Mic Gain: '+str(self.config['Module Mic'])],
            True)
            if response == '0': self.inputMenu('Module Power','',['Off','On','Tx Only','Rx Only'])
            elif response == '1': self.inputChar('Frequency 1',8)
            elif response == '1': self.inputChar('Frequency 2',8)
            elif response == '3': self.inputNums('Module Volume',9)
            elif response == '4': self.inputNums('Module Mic',8)
            else: break

    def menu_x1c5(self):
        while True:
            response = self.inputMenu('',"Selection:",
            ['Display Brightness: '+self.printEnum('Brightness',['Normal','Auto','High']),
            ' Backlight Timeout: '+str(self.config['Backlight Timeout']),
            '      Alert Enable: '+self.printEnum('Alert Enable'),
            '     Last Position: '+self.printEnum('Last Position'),
            ' Over 6 Knot No Tx: '+self.printEnum('Six Knots'),
            ' 30 min stop Alarm: '+self.printEnum('Stop 30m Alarm'),
            '  60 min Emergency: '+self.printEnum('Stop 60m Emergency')],
            True)
            if response == '0': self.inputMenu('Brightness', 'Brightness',['Normal','Auto','High'])
            elif response == '1': self.inputNums('Backlight Time',255)
            elif response == '2': self.toggleVal('Alert Enable')
            elif response == '3': self.toggleVal('Last Position')
            elif response == '4': self.toggleVal('Six Knots')
            elif response == '5': self.toggleVal('Stop 30m Alarm')
            elif response == '6': self.toggleVal('Stop 60m Emergency')
            else: break


########## Device routines
    def readSerialVersion(self):
        print("Reading Version...")  #debug print

        try:
            #open the serial port
            with serial.Serial(self.port, 9600, timeout=1) as ser:
                self.debug("Port open, reading")  #debug print
                # Send the command
                command = "AT+VER=?\r\n"
                ser.write(command.encode('utf-8'))
                # listen for the response
                byteString = ser.readline()
                response = byteString.decode('utf-8').split("|")
                self.debug("Response: "+str(response))  #debug print

                if len(byteString) < 10: return False
                self.version = response[0][6:]
                self.voltage = response[2][10:]
                return True

        except serial.SerialException as e:
            print("Error opening or using serial port:",e)
            return False

        self.debug("Exit readSerialVersion")  #debug print


    def readSerialDevice(self):
        print("Reading device...")  #debug print

        try:
            #open the serial port
            with serial.Serial(self.port, 9600, timeout=3) as ser:
                self.debug("Port open, reading")  #debug print
                # Send the read command
                command = "AT+SET=READ\r\n\n"
                ser.write(command.encode('utf-8'))
                # listen for the response
                self.raw = ser.read(517)  # read 517 bytes
                return True
        except serial.SerialException as e:
            print("Error opening or using serial port:",e)
            return False

        self.debug("Exit readSerialDevice")  #debug print

    def writeSerialDevice(self):
        print("Writing device...")  #debug print

        try:
            #open the serial port
            with serial.Serial(self.port, 9600, timeout=3) as ser:
                self.debug("Port open, writing")  #debug print
                # Send the read command
                command = bytes("AT+SET=WRITE",'utf-8')+self.raw[6:]   # exclude the 'HELLO' header
                self.debug("serial string="+str(command))
                ser.write(command)
                # listen for the response
                print('write response:', ser.read(1))
                return True
        except serial.SerialException as e:
            print("Error opening or using serial port:",e)
            return False

        self.debug("Exit writeSerialDevice")  #debug print


    def readIPDevice(self):
        # possible future feature!
        return
    def writeIPDevice(self):
        # possible future feature!
        return

########## Manipulating routines
    def compressConfig(self):
        # rebuild the bytestream from the dictionary, ensuring exact byte count and position
        # the bytestream is exactly 517 bytes of hexadecimal
        # once compressed it can be sent to the device or a file
        bytestring = b"HELLO"
        bytestring += self.intToHex('Time Value',2)
        bytestring += self.intToHex('Time Enable')
        bytestring += self.intToHex('Manual Enable')
        bytestring += self.intToHex('Smart')
        bytestring += self.intToHex('Queue Enable')
        bytestring += self.intToHex('Queue Time')
        bytestring += self.intToHex('PTT Delay')
        bytestring += self.encodeHex('CALLSIGN',7)
        bytestring += self.intToHex('SSID')
        bytestring += self.intToHex('MIC-E Enable')
        bytestring += self.intToHex('MIC-E Code')
        bytestring += self.encodeHex('Type',1)
        bytestring += self.encodeHex('Icon 1',2)
        bytestring += self.intToHex('BT Out 2')
        bytestring += self.intToHex('BT Out 1')
        bytestring += b'\x01\x00\x01\x01\x01\x01\x01\x01w' # unknown bytes
        bytestring += self.encodeHex('Latitude',10)
        bytestring += self.intToHex('Site Type')
        bytestring += self.intToHex('GPS Enable')
        bytestring += self.intToHex('Timezone Offset')
        bytestring += self.intToHex('GPS Save')
        bytestring += self.intToHex('Beep RX')
        bytestring += self.intToHex('Beep TX')
        bytestring += self.encodeHex('Longitude',10)
        bytestring += self.intToHex('BT Enable')
        bytestring += self.intToHex('Pressure Enable')
        bytestring += self.intToHex('Voltage Enable')
        bytestring += self.intToHex('Temperature Enable')
        bytestring += self.intToHex('Mileage Enable')
        bytestring += self.intToHex('Satellite Enable')
        bytestring += self.encodeHex('Message',62,)
        bytestring += b"\xff\xff" #
        bytestring += bytes('1,'+self.config['Frequency 1']+','+self.config['Frequency 2']+',0,3,0,0\r\n','utf-8')
        bytestring += b"\x00\xff\xff" # the tail end of the frequency string
        bytestring += self.intToHex('Module Power')
        bytestring += self.intToHex('Module Volume')
        bytestring += self.intToHex('Module Mic')
        bytestring += b'\x00'   #
        bytestring += self.intToHex('Auto Poweroff')
        bytestring += b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' #
        bytestring += self.intToHex('IP Protocol')
        bytestring += self.intToHex('IP Port',2)
        bytestring += b'\x00\x00\x00\x00\x00' #
        bytestring += self.intToHex('Odometer Enable')
        bytestring += self.encodeHex('Icon 2',2)
        bytestring += self.intToHex('Icon 2 Time',2)
        bytestring += self.encodeHex('IP Address',33)
        bytestring += b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'   # 10
        bytestring += b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'   # 10
        bytestring += b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'   # 10
        bytestring += b'\xff'   # 1
        bytestring += self.encodeHex('Wifi Name',16,b'\x00')
        bytestring += self.encodeHex('Wifi Code',16,b'\x00')
        bytestring += b'START1\x00\x01\x00' #
        bytestring += self.intToHex('Altitude',2)
        bytestring += b'\xff\xff\xff'
        bytestring += self.intToHex('Last Position')
        bytestring += self.intToHex('Six Knots')
        bytestring += self.intToHex('Stop 30m Alarm')
        bytestring += self.intToHex('Stop 60m Emergency')
        bytestring += b'\x01\x01\xff\xff\xff\xff\xff\xff\xff\xff\x08\x08\x08\x08\xc0\xa8\x01\x9b\xc0\xa8\x01\x01\xff\xff\xff\x00\xdc\x01\x02\t\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffo(\x9b\x7f\x11\x08E \xbd*\xad\x8eB^\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        bytestring += self.encodeHex('Emergency Message',32)
        bytestring += b'\x00'
        bytestring += self.intToHex('Brightness')
        bytestring += self.intToHex('Alert Enable')
        bytestring += self.intToHex('Volume TX')
        bytestring += self.intToHex('Volume RX')
        bytestring += self.intToHex('DIGI Delay')
        bytestring += self.intToHex('DIGI Channel')
        bytestring += self.intToHex('Beacon Channel')
        bytestring += self.encodeHex('Remote Code',7)
        bytestring += self.intToHex('Backlight Timeout')
        bytestring += self.encodeHex('PATH 1',7)
        bytestring += self.intToHex('PATH 1 Hops')
        bytestring += self.encodeHex('PATH 2',7)
        bytestring += self.intToHex('PATH 2 Hops')
        bytestring += self.encodeHex('DIGI 1',7)
        bytestring += self.intToHex('DIGI 1 Enable')
        bytestring += self.encodeHex('DIGI 2',7)
        bytestring += self.intToHex('DIGI 2 Enable')
#        bytestring += b'\x00' #
        self.raw = bytestring
        return bytestring


    def ExpandConfig(self):
        # parse the dictionary
        if True:
            # parse out all the bytes into their parts
            try:
                self.config['Header'] = self.raw[0:5].decode('utf-8')

                self.config['CALLSIGN'] = self.raw[13:20].decode('utf-8')
                self.config['SSID'] = ord(self.raw[20:21])
                self.config['MIC-E Enable'] = ord(self.raw[21:22])
                self.config['MIC-E Code'] = ord(self.raw[22:23])
                self.config['Site Type'] = ord(self.raw[47:48])
                self.config['Type'] = self.raw[23:24].decode('utf-8')

                self.config['Icon 1'] = self.raw[24:26].decode('utf-8')
                self.config['Icon 2'] = self.raw[193:195].decode('utf-8')
                self.config['Icon 2 Time'] = int.from_bytes(self.raw[195:197])

                self.config['BT Out 2'] = ord(self.raw[26:27])
                self.config['BT Out 1'] = ord(self.raw[27:28])
                self.config['BT Enable'] = ord(self.raw[62:63])

                self.config['GPS Enable'] = ord(self.raw[48:49])
                self.config['GPS Save'] = ord(self.raw[50:51])
                self.config['Latitude'] = self.raw[37:46].decode('utf-8')
                self.config['Longitude'] = self.raw[53:62].decode('utf-8')
                self.config['Altitude'] = int.from_bytes(self.raw[302:304], "big")

                self.config['Pressure Enable'] = ord(self.raw[63:64])
                self.config['Voltage Enable'] = ord(self.raw[64:65])
                self.config['Temperature Enable'] = ord(self.raw[65:66])
                self.config['Mileage Enable'] = ord(self.raw[66:67])
                self.config['Satellite Enable'] = ord(self.raw[67:68])
                self.config['Odometer Enable'] = ord(self.raw[192:193])
                self.config['Message'] = self.raw[69:132].strip(b'\xff\x00').decode('utf-8')
                self.config['Emergency Message'] = self.raw[436:468].strip(b'\xff\x00').decode('utf-8')
                self.config['Beacon Channel'] = ord(self.raw[476:477])

                self.config['Time Value'] = int.from_bytes(self.raw[5:7])
                self.config['Time Enable'] = ord(self.raw[7:8])
                self.config['Manual Enable'] = ord(self.raw[8:9])
                self.config['Smart'] = ord(self.raw[9:10])
                self.config['Queue Enable'] = ord(self.raw[10:11])
                self.config['Queue Time'] = ord(self.raw[11:12])
                self.config['PTT Delay'] = ord(self.raw[12:13])

                self.config['Wifi Name'] = self.raw[261:277].strip(b'\xff').decode('utf-8')
                self.config['Wifi Code'] = self.raw[277:293].strip(b'\x00').decode('utf-8')
                self.config['Wifi Enable'] = ord(self.raw[180:181])
                self.config['IP Address'] = self.raw[197:227].strip(b'').decode('utf-8')
                self.config['IP Protocol'] = ord(self.raw[184:185])
                self.config['IP Port'] = int.from_bytes(self.raw[185:187])

                self.config['Remote Code'] = self.raw[477:484].strip(b'\x00').decode('utf-8')
                self.config['PATH 1'] = self.raw[485:492].strip(b'\x00').decode('utf-8')
                self.config['PATH 1 Hops'] = ord(self.raw[492:493])
                self.config['PATH 2'] = self.raw[493:500].strip(b'\x00').decode('utf-8')
                self.config['PATH 2 Hops'] = ord(self.raw[500:501])
                self.config['DIGI 1'] = self.raw[501:508].strip(b'\x00').decode('utf-8')
                self.config['DIGI 1 Enable'] = ord(self.raw[508:509])
                self.config['DIGI 2'] = self.raw[509:516].strip(b'\x00').decode('utf-8')
                self.config['DIGI 2 Enable'] = ord(self.raw[516:517])
                self.config['DIGI Delay'] = ord(self.raw[474:475])
                self.config['DIGI Channel'] = ord(self.raw[475:476])

                self.config['Frequency 1'] = self.raw[135:143].decode('utf-8')
                self.config['Frequency 2'] = self.raw[144:152].decode('utf-8')
                self.config['Module Power'] = ord(self.raw[165:166])
                self.config['Module Volume'] = ord(self.raw[166:167])
                self.config['Module Mic'] = ord(self.raw[167:168])
                self.config['Beep RX'] = ord(self.raw[51:52])
                self.config['Beep TX'] = ord(self.raw[52:53])
                self.config['Volume TX'] = ord(self.raw[472:473])
                self.config['Volume RX'] = ord(self.raw[473:474])
                self.config['Beacon Channel'] = ord(self.raw[475:476])
                self.config['Auto Poweroff'] = ord(self.raw[169:170])

                self.config['Last Position'] = ord(self.raw[307:308])
                self.config['Six Knots'] = ord(self.raw[308:309])
                self.config['Stop 30m Alarm'] = ord(self.raw[309:310])
                self.config['Stop 60m Emergency'] = ord(self.raw[310:311])
                self.config['Brightness'] = ord(self.raw[470:471])
                self.config['Alert Enable'] = ord(self.raw[471:472])
                self.config['Backlight Timeout'] = ord(self.raw[484:485])
                self.config['Timezone Offset'] = ord(self.raw[49:50])

                self.parsed = True
            except UnicodeDecodeError:
                print("Config didn't load correctly!")
                time.sleep(2)
                self.parsed = False
        return

def main():

    # create the device object
    device = x1c3()

    # get the command line arguments
    parser = argparse.ArgumentParser(description='A tool to read and write configuration to the X1C3 APRS device', epilog='text at bottom')
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("--device_dump", action='store_true', help = "Read the settings from the device and dump to screen, non-interactive")
    parser.add_argument("--file_dump", action='store_true', help = "Read the settings from the device and dump to screen, non-interactive")
    parser.add_argument("-r", "--read", action='store_true', help = "Read the settings directly into the file, non-interactive")
    parser.add_argument("-w", "--write", action='store_true', help = "Write the settings directly into the device, non-interactive")
    parser.add_argument("-p", "--port", nargs='?', default='/dev/ttyUSB0', help = "Set the port")
    parser.add_argument("-ef", "--edit_file", action='store_true', help = "Load the file and parse it, go straight into edit menu")
    parser.add_argument("-ed", "--edit_device", action='store_true', help = "Load the device and parse it, go straight into edit menu")
    parser.add_argument("-f", "--file", nargs='?', default='settings.sav', help = "Set the file")
    parser.add_argument("--test",action='store_true')

    args = parser.parse_args()

    device.setFile(args.file)
    device.setPort(args.port)
    device.debugFlag = args.verbose

    device.debug("Using file: "+str(args.file))  #debug print
    device.debug("Using port: "+str(args.port))  #debug print
    device.debug("Read: "+str(args.read))        #debug print
    device.debug("Write: "+str(args.write))      #debug print

    action = ''
    # if the user passed args to read or write the config non-interactivly, just do that and exit\
    # but first test that we can read the version from the device!
    if args.read:
        if device.readSerialVersion():
            device.readSerialDevice() # read the config from device
            device.writeFile()  # write the config to file
            action = 'q'       # exit the program
        else:
            print("Failed to connect to device!")
        sys.exit()

    # command line only to read config from file and write to device
    if args.write:
        if device.readSerialVersion():
            device.readFile()    # read the config from file
            device.writeSerialDevice() # write the config to device
        else:
            print("Failed to connect to device!")
        sys.exit()

    # read the device, print it, and exit
    if args.device_dump:
        if device.readSerialDevice():
            print('bytes read=',len(device.raw))
            device.printraw()
        else: print("Can't read device!")
        sys.exit()

    # read the file, print it, and exit
    if args.file_dump:
        if device.readFile():    # read the config from file
            print('bytes read=',len(device.raw))
            device.printRaw()
        else: print("Can't read file!")
        sys.exit()

    # Open a device, the parse it autmoatically before going to the main menu
    if args.edit_device:
        if  device.readSerialVersion():
            device.readSerialDevice()    # read the config from device
            device.ExpandConfig()   # parse out the data
            action = '6'

    # Open a file, the parse it autmoatically before going to the main menu
    if args.edit_file:
        if device.readFile():    # read the config from file
            device.ExpandConfig() # parse out the data
            device.compressConfig()
            action = '6'

    if args.test:
        # do what you need to test
        print("running test...")
        device.readSerialDevice()
        device.printRaw()
        print("Parsing...")
        device.ExpandConfig()
        print("compressing...")
        device.compressConfig()
        device.printRaw()
        print("test done!")
        sys.exit()

    # main program loop
    while action != 'q':
        device.debug("MainLoop start")  #debug print

        if action == '':
            action = device.inputMenu('',"Selection:",['Read from device','Write to device','Read from file','Write to file','Port: '+device.getPort(),'File: '+device.getFile(),'Edit Config','Print Config'],True)

        #device.debug("Action="+ action)  #debug print

        if action == '0':   #read device
            if device.readSerialVersion():
                device.readSerialDevice()
                device.ExpandConfig()
            else:
                print("Failed to connect to device!")
                time.sleep(2)

        if action == '1':   #write device
            if device.hasConfig():
                device.compressConfig()
                device.writeSerialDevice()
                print("Written!")
            else:
                print("No Config loaded!")
            time.sleep(2)

        if action == '2':   #read file
            if device.readFile():
                print("Reading file...")
                device.ExpandConfig()
                print("File read!")
            else:
                print("Could not read file!")
            time.sleep(2)

        if action == '3':   #write file
            if device.hasConfig():
                print("Writing file...")
                device.compressConfig()
                device.writeFile()
                print("Written!")
            else:
                print("No Config loaded!")
            time.sleep(2)

        if action == '4':   #set the port
            response = input("Port:"+device.getPort())
            if not device.setPort(response):
                # invalid port
                device.setPort("Invalid")
                print("Invalid port!")
                time.sleep(2)

        if action == '5':   #set the file
            response = input("File:"+device.getFile())
            if not device.setFile(response):
                # invalid file
                device.setFile("Invalid")
                print("Invalid file!")
                time.sleep(2)

        if action == '6':   #edit menu
            if device.hasConfig():
                device.editMenu()
            else:
                print("No Config loaded!")
                time.sleep(2)

        if action == '7':   #print config
            if device.hasConfig():
                device.printConfig()
            else:
                print("No Config loaded!")
                time.sleep(2)

        if action == "q": break
        action = ''   #reset the next action
    # end of menu while

    device.debug("End of program")  #debug print
    print("")


if __name__ == "__main__":
    main()
