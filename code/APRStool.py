import serial
import time
import argparse
import os
import sys
#import pyinputplus as pyip

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


########## File routines
    def debug(self, message):
        if self.debugFlag: print(message)

    def setPort(self,name):
        # set the port name
        # test if the port exists. set name=Invalid if it's a bad port
        self.port = name
        return True

    def hasConfig(self):
        # return true if the config dictionary has contents
        #if debug: print("hasConfig=", str(bool(self.config)))  #debug print
        return bool(len(self.raw) > 0)

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

    def toBS(self,param):
        # Convert the integer to a hexadecimal string.
        # this works with multi-byte numbers
        hex_str = hex(self.config[param])[2:]  # Remove the '0x' prefix
        # Pad with zeros if necessary to ensure an even number of hex digits
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str
        # Convert the hex string to bytes
        return bytes.fromhex(hex_str)

########## File routines
    def readFile(self):
        # read the config string from the file in to self.raw
        print("Reading file...")
        with open(self.file, "rb") as f:
            self.raw = f.read()
        return True

    def writeFile(self):
        # write the raw config string from the self.raw to the file
        print("Writing file...")
        with open(self.file, "wb") as f:
            f.write(self.raw)
        print("Written!")
        time.sleep(2)
        return True

    def setFile(self,name):
        # set the file name
        # test if the file exists or can be created. set name=Invalid if it's a bad file
        self.file = name
        return True

########## Menu routines
    def menuHeader(self):
        os.system('clear')
        print("--------------------------------")
        print("X1C3 Configuration Tool - KG7KMV")
        print("")
        print("Device FW Version:", self.version)
        print("   Device Voltage:", self.voltage)
        print("    Config loaded:", self.hasConfig())
        print("--------------------------------")

    def printEnum(self,num,options):
        print("num=",num)
        print("options=",options)
        return options[int(num)]

    def inputMenu(self,prompt,options,quit=False):
        #print the header, options, and a prompt. Return a number string with the selection
        self.menuHeader()
        for i in range(len(options)):
            print(i,'-',options[i],' ')
        if quit: print("q - Exit")
        print("--------------------------------")
        return input(prompt)

    def mainMenu(self):
        # create a user menu to run the program
        self.debug("Start mainMenu")  #debug print
        response = self.inputMenu("Selection:",['Read from device','Write to device','Read from file','Write to file','Port: '+self.port,'File: '+self.file,'Edit Config','Print Config'],True)
        self.debug("Exit mainMenu")  #debug print
        return response

    def editMenu(self):
        self.debug("Start editMenu")  #debug print
        # create a user menu to run the program
        while True:
            response = self.inputMenu("Selection:",['Setup','Beacon','Bluetooth','Fixed','WiFi','Digpeater','Audio','RF Module'],True)
            if response == '0': self.menu_setup()
            elif response == '1': self.menu_beacon()
            elif response == '2': self.menu_bluetooth()
            elif response == '3': self.menu_fixed()
            elif response == '4': self.menu_wifi()
            elif response == '5': self.menu_digi()
            elif response == '6': self.menu_audio()
            elif response == '7': self.menu_rfmodule()
            else: break

    def menu_setup(self):
        while True:
            response = self.inputMenu("Selection:",
                ['   Callsign: '+self.config['CALLSIGN'],
                '       SSID: '+str(self.config['SSID']),
                '  Site Type: '+self.printEnum(self.config['Site'],['Fixed','Mobile','Weather']),
                '        GPS: '+self.printEnum(self.config['GPS Enable'],['Enabled','Disabled']),
                '     Icon 1: '+self.config['Icon 1'],
                '     Icon 2: '+self.config['Icon 2'],
                'Icon 2 Time: '+str(self.config['Icon 2 Time'])],
                True)
            if response == '0': self.config['CALLSIGN'] = input("Callsign(<7 chars):")
            elif response == '1': self.config['SSID'] = self.inputMenu("SSID:",['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15'])
            elif response == '2': self.config['Site'] = self.inputMenu("Site Type:",['Fixed','Mobile','Weather'])
            elif response == '3': self.config['GPS Enable'] = self.inputMenu("GPS:",['Disable','Enable'])
            elif response == '4': self.config['Icon 1'] = input("Icon 1 (2 chars):")
            elif response == '5': self.config['Icon 2'] = input("Icon 2 (2 chars):")
            elif response == '6': self.config['Icon 2 Time'] = input("Icon 2 Time (0-999s):")
            else: break

    def menu_beacon(self):
        while True:
            response = self.inputMenu("Selection:",
            ['   Smart Beacon: '+self.printEnum(self.config['Smart'],['OFF','1','2','3','4','5']),
            '  Manual Enable: '+self.printEnum(self.config['Manual Enable'],['Disable','Enable']),
            '       GPS Save: '+self.printEnum(self.config['GPS Save'],['Disable','Enable']),
            '   Queue Enable: '+self.printEnum(self.config['Queue Enable'],['Disable','Enable']),
            '     Queue Time: '+str(self.config['Queue Time']),
            '    Time Enable: '+self.printEnum(self.config['Time Enable'],['Disable','Enable']),
            '           Time: '+str(self.config['Time Value']),
            '   MIC-E Enable: '+self.printEnum(self.config['MIC-E Enable'],['Disable','Enable']),
            '     MIC-E Code: '+self.printEnum(self.config['MIC-E Code'],['Off Duty','En Route','In Service','Returning','Committed','Special','Priority','Emergency']),
            '        Message: '+self.config['Message'],
            '    Add Mileage: '+self.printEnum(self.config['Mileage Enable'],['Disable','Enable']),
            '   Add Pressure: '+self.printEnum(self.config['Pressure Enable'],['Disable','Enable']),
            '    Add Voltage: '+self.printEnum(self.config['Voltage Enable'],['Disable','Enable']),
            'Add Temperature: '+self.printEnum(self.config['Temperature Enable'],['Disable','Enable']),
            ' Add Satellites: '+self.printEnum(self.config['Satellite Enable'],['Disable','Enable']),
            '   Add Odometer: '+self.printEnum(self.config['Odometer Enable'],['Disable','Enable'])],
            True)
            if response == '0': self.config['Smart'] = self.inputMenu('Smart Beacon:',['OFF','1','2','3','4','5'])
            elif response == '1': self.config['Manual Enable'] = self.inputMenu("Manual Enable:",['Disable','Enable'])
            elif response == '2': self.config['GPS Save'] = self.inputMenu("GPS Save:",['Disable','Enable'])
            elif response == '3': self.config['Queue Enable'] = self.inputMenu("Queue Enable:",['Disable','Enable'])
            elif response == '4': self.config['Queue Time'] = input("Queue Time (<9999s):")
            elif response == '5': self.config['Time Enable'] = self.inputMenu("Time Enable:",['Disable','Enable'])
            elif response == '6': self.config['Time Value'] = input("Time Value (<9999s):")
            elif response == '7': self.config['MIC-E Enable'] = self.inputMenu("MIC-E Enable:",['Disable','Enable'])
            elif response == '8': self.config['MIC-E Code'] = self.inputMenu("MIC-E Code:",['Off Duty','En Route','In Service','Returning','Committed','Special','Priority','Emergency'])
            elif response == '9': self.config['Message'] = input('Message (<60 chars):')
            elif response == '10': self.config['Mileage Enable'] = self.inputMenu("Add Mileage:",['Disable','Enable'])
            elif response == '11': self.config['Pressure Enable'] = self.inputMenu("Add Pressure:",['Disable','Enable'])
            elif response == '12': self.config['Voltage Enable'] = self.inputMenu("Add Voltage:",['Disable','Enable'])
            elif response == '13': self.config['Temperature Enable'] = self.inputMenu("Add Temperature:",['Disable','Enable'])
            elif response == '14': self.config['Satellite Enable'] = self.inputMenu("Add Satellites:",['Disable','Enable'])
            elif response == '15': self.config['Odometer Enable'] = self.inputMenu("Add Odometer:",['Disable','Enable'])
            else: break

    def menu_bluetooth(self):
        while True:
            response = self.inputMenu("Selection:",
            [' BT Out 1: '+self.printEnum(self.config['BT Out 1'],['Off','KISS hex','UI','GPWPL','KISS ascii']),
            ' BT Out 2: '+self.printEnum(self.config['BT Out 2'],['Off','GPS','Rotator']),
            ' BT Enable: '+self.printEnum(self.config['BT Enable'],['Disable','Enable'])],
            True)
            if response == '0': self.config['BT Out 1'] = self.inputMenu("BT Out 1:",['Off','KISS hex','UI','GPWPL','KISS ascii'])
            elif response == '1': self.config['BT Out 2'] = self.inputMenu("BT Out 2:",['Off','GPS','Rotator'])
            elif response == '2': self.config['BT Enable'] = self.inputMenu("BT Enable:",['Disable','Enable'])
            else: break

    def menu_fixed(self):
        while True:
            response = self.inputMenu("Selection:",
            [' Latitude: '+str(self.config['Latitude']),
            'Longitude: '+str(self.config['Longitude']),
            ' Altitude: '+str(self.config['Altitude'])],
            True)
            if response == '0': self.config['Latitude'] = input('Latitude (xxx.xxN):')
            elif response == '1': self.config['Longitude'] = input('Longitude (xxx.xxW):')
            elif response == '2': self.config['Altitude'] = input('Altitude (<9999m):')
            else: break

    def menu_digi(self):
        while True:
            response = self.inputMenu("Selection:",
            ['Digi 1 Enable: '+self.printEnum(self.config['DIGI 1 Enable'],['Disable','Enable']),
            '  Digi 1 PATH: '+self.config['DIGI 1'],
            'Digi 2 Enable: '+self.printEnum(self.config['DIGI 2 Enable'],['Disable','Enable']),
            '  Digi 2 PATH: '+self.config['DIGI 2'],
            '   Digi Delay: '+str(self.config['DIGI Delay']),
            ' Digi Channel: '+self.printEnum(self.config['DIGI CH'],['CH A','CH B','CH A+B','Bluetooth'])],
            True)
            if response == '0': self.config['DIGI 1 Enable'] = self.inputMenu("Digi 1 Enable:",['Disable','Enable'])
            elif response == '1': self.config['DIGI 1'] = input('Digi 1 Path:')
            elif response == '2': self.config['DIGI 2 Enable'] = self.inputMenu("Digi 2 Enable:",['Disable','Enable'])
            elif response == '3': self.config['DIGI 2'] = input('Digi 2 Path:')
            elif response == '4': self.config['DIGI Delay'] = self.inputMenu('Digi Delay ',['0s','1s','2s','3s','4s','5s'])
            elif response == '5': self.config['DIGI CH'] = self.inputMenu("Digi CH:",['CH A','CH B','CH A+B','Bluetooth'])
            else: break

    def menu_wifi(self):
        selection = ''
        while True:
            response = self.inputMenu("Selection:",
            ['    WiFI SSID: '+str(self.config['Wifi Name']),
            'WiFI Password: '+str(self.config['Wifi Code']),
            '  WiFi Enable: '+self.printEnum(self.config['Wifi Enable'],['Disable','Enable']),
            '   IP Address: '+str(self.config['IP Address']),
            '      IP Port: '+str(self.config['IP Port']),
            '  IP Protocol: '+self.printEnum(self.config['IP Protocol'],['UDP','TCP'])],
            True)
            if response == '0': self.config['Wifi Name'] = input('WiFi Name (<16 char):')
            elif response == '1': self.config['Wifi Code'] = input("WiFi Password (<16 char):")
            elif response == '2': self.config['Wifi Enable'] = self.inputMenu("WiFi Enable:",['Disable','Enable'])
            elif response == '3': self.config['IP Address'] = input("IP Address (<? char):")
            elif response == '4': self.config['IP Port'] = input("Port (<6 char):")
            elif response == '5': self.config['IP Protocol'] = self.inputMenu("Protocol:",['TCP','UDP'])
            else: break

    def menu_audio(self):
        while True:
            response = self.inputMenu("Selection:",
            ['Tx Volume: '+self.printEnum(self.config['Volume TX'],['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB']),
            'Rx Volume: '+self.printEnum(self.config['Volume RX'],['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB']),
            '  Tx Beep: '+self.printEnum(self.config['Beep TX'],['Disable','Enable']),
            '  Rx Beep: '+self.printEnum(self.config['Beep RX'],['Disable','Enable'])],
            True)
            if response == '0': self.config['Volume TX'] = self.inputMenu('Tx Volume',['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB'])
            elif response == '1': self.config['Volume RX'] = self.inputMenu('Rx Volume',['-10.5dB','-9.0dB','-7.5dB','-6.0dB','-4.5dB','-3.0dB','-1.5dB','0dB'])
            elif response == '2': self.config['Beep TX'] = self.inputMenu("Beep TX:",['Disable','Enable'])
            elif response == '3': self.config['Beep RX'] = self.inputMenu("Beep Rx:",['Disable','Enable'])
            else: break

    def menu_rfmodule(self):
        while True:
            response = self.inputMenu("Selection:",
            ['      Power: '+self.printEnum(self.config['Module Power'],['Off','On','Tx Only','Rx Only']),
            'Frequency 1: '+str(self.config['Frequency 1']),
            'Frequency 2: '+str(self.config['Frequency 2']),
            '     Volume: '+str(self.config['Module Volume']),
            '   Mic Gain: '+str(self.config['Module Mic'])],
            True)
            if response == '0': self.config['Module Power'] = self.inputMenu('RF Module Power',['Off','On','Tx Only','Rx Only'])
            elif response == '1': self.config['Frequency 1'] = input('Frequency 1 (xxx.xxxx):')
            elif response == '1': self.config['Frequency 2'] = input('Frequency 1 (xxx.xxxx):')
            elif response == '3': self.config['Module Volume'] = input('Speaker Volume (1-9):')
            elif response == '4': self.config['Module Mic'] = input('Mic Gain (1-8):')
            else: break


########## Device routines
    def readVersion(self):
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

        self.debug("Exit readVersion")  #debug print


    def readDevice(self):
        print("Reading device...")  #debug print

        try:
            #open the serial port
            with serial.Serial(self.port, 9600, timeout=3) as ser:
                self.debug("Port open, reading")  #debug print
                # some establish time
                #time.sleep(1)
                # Send the command
                command = "AT+SET=READ\r\n\n"
                ser.write(command.encode('utf-8'))
                # listen for the response
                self.raw = ser.read(517)  # read 517 bytes
                return True
        except serial.SerialException as e:
            print("Error opening or using serial port:",e)
            return False

        self.debug("Exit readDevice")  #debug print

########## Manipulating routines
    def compressConfig(self):
        # rebuild the bytestream from the dictionary, ensuring exact byte count and position
        # the bytestream is exactly 517 bytes of hexadecimal
        # once compressed it can be sent to the device or a file
        bytestring = b"HELLO"
        bytestring += self.toBS('Time Value')
        bytestring += self.toBS('Time Enable')
        bytestring += self.toBS('Manual Enable')
        bytestring += self.toBS('Smart')
        bytestring += self.toBS('Queue Enable')
        bytestring += self.toBS('Queue Time')
        bytestring += self.toBS('PTT Delay')
        bytestring += self.encodeHex('CALLSIGN',7)
        bytestring += self.toBS('SSID')
        bytestring += self.toBS('MIC-E Enable')
        bytestring += self.toBS('MIC-E Code')
        bytestring += self.encodeHex('Type',1)
        bytestring += self.encodeHex('Icon 1',2)
        bytestring += self.toBS('BT Out 2')
        bytestring += self.toBS('BT Out 1')
        bytestring += b'\x00\x00\x00\x00\x00\x00\x00\x00' #
        bytestring += self.encodeHex('Latitude',10)
        bytestring += self.toBS('Site')
        bytestring += self.toBS('GPS Enable')
        bytestring += b'\x15' #
        bytestring += self.toBS('GPS Save')
        bytestring += self.toBS('Beep RX')
        bytestring += self.toBS('Beep TX')
        bytestring += self.encodeHex('Longitude',10)
        bytestring += self.toBS('BT Enable')
        bytestring += self.toBS('Pressure Enable')
        bytestring += self.toBS('Voltage Enable')
        bytestring += self.toBS('Temperature Enable')
        bytestring += self.toBS('Mileage Enable')
        bytestring += self.toBS('Satellite Enable')
        bytestring += self.encodeHex('Message',60)
        bytestring += b"\xff\xff\xff\xff" #
        bytestring += bytes('1,'+self.config['Frequency 1']+','+self.config['Frequency 2']+',0,3,0,0\r\n','utf-8')
        bytestring += b"\x00\xff\xff" #
        bytestring += self.toBS('Module Power')
        bytestring += self.toBS('Module Volume')
        bytestring += self.toBS('Module Mic')
        bytestring += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' #
        bytestring += self.toBS('IP Protocol')
        bytestring += self.toBS('IP Port')
        bytestring += b'\x00\x00\x00\x00\x00\x00' #
        bytestring += self.encodeHex('Icon 2',2)
        bytestring += self.toBS('Icon 2 Time')
        bytestring += b'\xb4' #
        bytestring += self.encodeHex('IP Address',30)
        bytestring += b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' #
        bytestring += self.encodeHex('Wifi Name',16)
        bytestring += self.encodeHex('Wifi Code',16)
        bytestring += b'START1\x00\x01\x00\x00' #
        bytestring += self.toBS('Altitude')
        bytestring += b'\xff\xff\xff\x00\x00\x00\x00\x01\x01\xff\xff\xff\xff\xff\xff\xff\xff\x08\x08\x08\x08\xc0\xa8\x01\x9b\xc0\xa8\x01\x01\xff\xff\xff\x00\xdc\x01\x02\t\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffo(\x9b\x7f\x11\x08E \xbd*\xad\x8eB^\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        bytestring += self.encodeHex('Emergency Message',32)
        bytestring += b'\x00\x00\x00'
        bytestring += self.toBS('Volume TX')
        bytestring += self.toBS('Volume RX')
        bytestring += b'\x00' #
        bytestring += self.toBS('Beacon Channel')
        bytestring += b'\x00' #
        bytestring += self.encodeHex('Remote Code',7)
        bytestring += self.toBS('DIGI Delay')
        bytestring += self.encodeHex('PATH 1',7)
        bytestring += self.toBS('PATH 1 Hops')
        bytestring += self.encodeHex('PATH 2',7)
        bytestring += self.toBS('PATH 2 Hops')
        bytestring += self.encodeHex('DIGI 1',7)
        bytestring += self.toBS('DIGI 1 Enable')
        bytestring += self.encodeHex('DIGI 2',7)
        bytestring += self.toBS('DIGI 2 Enable')
#        bytestring += b'\x00' #


        print('compressed=',bytestring)


    def parseConfig(self):
        # parse the dictionary
#        if not self.parsed: 
            print("Parsing...")  #debug print

            # parse out all the bytes into their parts
            try:
                self.config['Header'] = self.raw[0:5].decode('utf-8')

                self.config['CALLSIGN'] = self.raw[13:20].decode('utf-8')
                self.config['SSID'] = ord(self.raw[20:21])
                self.config['MIC-E Enable'] = ord(self.raw[21:22])
                self.config['MIC-E Code'] = ord(self.raw[22:23])
                self.config['Site'] = ord(self.raw[47:48])
                self.config['Type'] = self.raw[23:24].decode('utf-8')

                self.config['Icon 1'] = self.raw[24:26].decode('utf-8')
                self.config['Icon 2'] = self.raw[193:195].decode('utf-8')
                self.config['Icon 2 Time'] = ord(self.raw[195:196])

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
                self.config['Message'] = self.raw[69:132].strip(b'\xff').decode('utf-8')
                self.config['Emergency Message'] = self.raw[436:468].strip(b'\xff').decode('utf-8')
                self.config['Beacon Channel'] = ord(self.raw[475:476])

                self.config['Time Value'] = int.from_bytes(self.raw[5:7])
                self.config['Time Enable'] = ord(self.raw[7:8])
                self.config['Manual Enable'] = ord(self.raw[8:9])
                self.config['Smart'] = ord(self.raw[9:10])
                self.config['Queue Enable'] = ord(self.raw[10:11])
                self.config['Queue Time'] = ord(self.raw[11:12])
                self.config['PTT Delay'] = ord(self.raw[12:13])

                self.config['Wifi Name'] = self.raw[261:277].strip(b'\xff').decode('utf-8')
                self.config['Wifi Code'] = self.raw[277:293].strip(b'\x00').decode('utf-8')
                self.config['Wifi Enable'] = ord(self.raw[64:65]) # wrong
                self.config['IP Address'] = self.raw[197:227].strip(b'\x00').decode('utf-8')
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
                self.config['DIGI Channel'] = ord(self.raw[475:476]) # wrong

                self.config['Frequency 1'] = self.raw[135:143].decode('utf-8')
                self.config['Frequency 2'] = self.raw[144:152].decode('utf-8')
                self.config['Module Power'] = ord(self.raw[165:166])
                self.config['Module Volume'] = ord(self.raw[166:167])
                self.config['Module Mic'] = ord(self.raw[167:168])
                self.config['Beep RX'] = ord(self.raw[51:52])
                self.config['Beep TX'] = ord(self.raw[52:53])
                self.config['Volume TX'] = ord(self.raw[472:473])
                self.config['Volume RX'] = ord(self.raw[473:474])

                self.parsed = True
            except UnicodeDecodeError:
                print("Config didn't load correctly!")
                time.sleep(3)
                self.parsed = False

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
    parser.add_argument("-pf", "--parse_file", action='store_true', help = "Load the file and parse it")
    parser.add_argument("-pd", "--parse_device", action='store_true', help = "Load the device and parse it")
    parser.add_argument("-f", "--file", nargs='?', default='settings.sav', help = "Set the file")

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
        if device.readVersion():
            device.readDevice() # read the config from device
            device.writeFile()  # write the config to file
            action = 'q'       # exit the program
        else:
            print("Failed to connect to device!")
        sys.exit()

    # command line only to read config from file and write to device
    if args.write:
        if device.readVersion():
            device.readFile()    # read the config from file
            device.writeConfig() # write the config to device
        else:
            print("Failed to connect to device!")
        sys.exit()

    # read the device, print it, and exit
    if args.device_dump:
        device.readDevice()
        print('bytes read=',len(device.raw))
        print('bytes=',device.raw)
        sys.exit()

    # read the file, print it, and exit
    if args.file_dump:
        device.readFile()    # read the config from file
        print('bytes read=',len(device.raw))
        print('bytes=',device.raw)
        sys.exit()

    # Open a device, the parse it autmoatically before going to the main menu
    if args.parse_device:
        if  device.readVersion():
            device.readDevice()    # read the config from device
            device.parseConfig()   # parse out the data
            action = '6'

    # Open a file, the parse it autmoatically before going to the main menu
    if args.parse_file:
        if device.readFile():    # read the config from file
            device.parseConfig() # parse out the data
            device.compressConfig()
            print('output:'+device.raw)
            action = 'q'

    # main program loop
    while True:
        device.debug("MainLoop start")  #debug print

        if action == '': action = device.mainMenu()
        device.debug("Action="+ action)  #debug print

        if action == '0':   #read device
            if not device.readVersion():
                print("Failed to connect to device!")
                break
            device.readDevice()
            device.parseConfig()

        if action == '1':   #write device
            if device.hasConfig():
                device.compressConfig()
                device.writeConfig()
            else:
                print("No Config loaded!")
                time.sleep(3)

        if action == '2':   #read file
            device.readFile()
            device.parseConfig()

        if action == '3':   #write file
            if device.hasConfig():
                device.compressConfig()
                device.writeFile()
            else:
                print("No Config loaded!")
                time.sleep(3)

        if action == '4':   #set the port
            response = input("Port:")
            if not device.setPort(response):
                # invalid port
                device.setPort("Invalid")
                print("Invalid port!")
                time.sleep(3)

        if action == '5':   #set the file
            response = input("File:")
            if not device.setFile(response):
                # invalid file
                device.setFile("Invalid")
                print("Invalid file!")
                time.sleep(3)

        if action == '6':   #edit menu
            if device.hasConfig():
                device.editMenu()
            else:
                print("No Config loaded!")
                time.sleep(3)

        if action == '7':   #print config
            if device.hasConfig():
                device.printConfig()
            else:
                print("No Config loaded!")
                time.sleep(3)

        if action == '8':   #secret menu item to print raw, same as --dump_device or --dump_file 
            device.compressConfig()
            print('raw=',device.raw)
            time.sleep(10)

        if action == "q": break
        action = ''   #reset the next action
    # end of menu while

    device.debug("End of program")  #debug print
    print("")


if __name__ == "__main__":
    main()
