"""P1 adapter for WebThings Gateway."""

import os
from os import path
import sys
sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))

#import json
#import asyncio
#import logging
import threading

import serial
import serial.tools.list_ports as prtlst

import time
from time import sleep

from gateway_addon import Adapter, Device, Property, Action, Database
from .util import pretty, is_a_number, get_int_or_float

from smeterd.meter import SmartMeter

#from smeterd.meter import SmartMeterError
#from .tests import SerialMock
#from .tests import NORMAL_PACKET
#from .tests import BROKEN_PACKET
#from .tests import LONG_BROKEN_PACKET
#from .tests import NORMAL_PACKET_1003



_TIMEOUT = 3

_CONFIG_PATHS = [
    os.path.join(os.path.expanduser('~'), '.webthings', 'config'),
]

if 'WEBTHINGS_HOME' in os.environ:
    _CONFIG_PATHS.insert(0, os.path.join(os.environ['WEBTHINGS_HOME'], 'config'))




class P1Adapter(Adapter):
    """Adapter for P1"""

    def __init__(self, verbose=True):
        """
        Initialize the object.

        verbose -- whether or not to enable verbose logging
        """
        print("Initialising P1 adapter")
        self.pairing = False
        self.name = self.__class__.__name__
        self.addon_name = 'p1-adapter'
        Adapter.__init__(self, 'p1-adapter', 'p1-adapter', verbose=verbose)
        #print("Adapter ID = " + self.get_id())

        self.addon_path = os.path.join(self.user_profile['addonsDir'], self.addon_name)

        self.DEBUG = True
        self.first_request_done = False
        self.initial_serial_devices = []
        self.running = True
        self.usb_override = False
        self.usb_port = "/dev/ttyUSB0"
        
        self.previous_consumed_total = None
        self.previous_produced_total = None
        self.previous_gas_total = None
        
        try:
            self.scan_usb_ports()
        except:
            print("Error during scan of usb ports")
            
        
        try:
            self.add_from_config()
        except Exception as ex:
            print("Error loading config (and initialising PyP1 library?): " + str(ex))

        
        # If only one USB serial device is available, we pick that one anyway, regardless of what the user has selected in the config.
        try:
            if len(self.initial_serial_devices) == 1 and self.usb_override == False:
                self.usb_port = self.initial_serial_devices[0]
                print("only one Serial USB device found, selecting that one.")
        except Exception as ex:
            print("Error with auto selection of USB port: " + str(ex))
        

        try:
            print("Attempting to start P1 connection with USB port: " + self.usb_port)
            self.meter = SmartMeter(self.usb_port)
            #print("self.meter is now: " + str(self.meter))
            
            try:
                # Create the p1 device, and if succesful, start the internal clock
                try:
                    p1_device = P1Device(self)
                    self.handle_device_added(p1_device)
                    self.devices['p1-device'].connected = True
                    self.devices['p1-device'].connected_notify(True)
                    self.thing = self.get_device("p1-device")
                
                
                    # Start the clock
                    if self.DEBUG:
                        print("Starting the internal clock")
                    try:
                        t = threading.Thread(target=self.clock)
                        t.daemon = True
                        t.start()
                    except:
                        print("Error starting the clock thread")
                
                except Exception as ex:
                    print("Could not create p1_device: " + str(ex))
            
            
            except Exception as ex:
                print("Error starting p1 meter: " + str(ex))
            
        except Exception as ex:
            print("Error loading serial: " + str(ex))


        

        print("End of P1 adapter init process")
        




    def clock(self):
        """ Runs every minute and updates which devices are still connected """
        if self.DEBUG:
            print("clock thread init")
            
        seconds_counter = 50;
        minutes_counter = 0;
        while self.running:
            try:
                current_time = int(time.time())
                if self.DEBUG:
                    print("CLOCK TICK " + str(current_time) )
          
                packet = self.meter.read_one_packet()
                if self.DEBUG:
                    print("packet = " + str(packet))
                
                property_counter_before = len(self.thing.properties)





                #
                #  KWH
                #

                try:
                    kwh = packet['kwh']
                    
                    if self.DEBUG:
                        print("--------KWH---------")
    
                        for key, value in kwh.items():
                            print(key, ' : ', value)
    
                        print("--------------------")
                    
                    if 'low' in kwh:
                        if 'consumed' in kwh['low']:
                            targetProperty = self.thing.find_property('kwh-low-consumed')
                            if targetProperty == None:
                                if self.DEBUG:
                                    print("-property did not exist yet. Creating it now.")
                                self.thing.properties["kwh-low-consumed"] = P1Property(
                                                self.thing,
                                                "kwh-low-consumed",
                                                {
                                                    'label': "Low consumed",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                kwh['low']['consumed'])
                                targetProperty = self.thing.find_property('kwh-low-consumed')
                                
                            new_value = get_int_or_float(kwh['low']['consumed'])
                            targetProperty.update(new_value)
                                    
                        if 'produced' in kwh['low']:
                            targetProperty = self.thing.find_property('kwh-low-produced')
                            if targetProperty == None:
                                self.thing.properties["kwh-low-produced"] = P1Property(
                                                self.thing,
                                                "kwh-low-produced",
                                                {
                                                    'label': "Low produced",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                kwh['low']['produced'])
                                targetProperty = self.thing.find_property('kwh-low-produced')
                                
                            new_value = get_int_or_float(kwh['low']['produced'])
                            targetProperty.update(new_value)
                                
                                
                    if 'high' in kwh:
                        if 'consumed' in kwh['high']:
                            targetProperty = self.thing.find_property('kwh-high-consumed')
                            if targetProperty == None:
                                self.thing.properties["kwh-high-consumed"] = P1Property(
                                                self.thing,
                                                "kwh-high-consumed",
                                                {
                                                    'label': "High consumed",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                kwh['high']['consumed'])
                                targetProperty = self.thing.find_property('kwh-high-consumed')
                                                
                            new_value = get_int_or_float(kwh['high']['consumed'])
                            targetProperty.update(new_value)  

                        if 'produced' in kwh['high']:
                            targetProperty = self.thing.find_property('kwh-high-produced')
                            if targetProperty == None:
                                self.thing.properties["kwh-high-produced"] = P1Property(
                                                self.thing,
                                                "kwh-high-produced",
                                                {
                                                    'label': "High produced",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                kwh['high']['produced'])
                            
                                targetProperty = self.thing.find_property('kwh-high-produced')
                            
                            new_value = get_int_or_float(kwh['high']['produced'])
                            targetProperty.update(new_value)


                    if 'high' in kwh:
                        if 'consumed' in kwh['high']:
                            if 'low' in kwh:
                                if 'consumed' in kwh['low']:
                                    consumed_total = get_int_or_float(kwh['high']['consumed']) + get_int_or_float(kwh['low']['consumed'])
                                    if self.DEBUG:
                                        print("total consumed = " + str(consumed_total))
                                    
                                    if self.previous_consumed_total == None:
                                        self.previous_consumed_total = consumed_total
                                    
                                    targetProperty = self.thing.find_property('kwh-total-consumed')
                                    if targetProperty == None:
                                        self.thing.properties["kwh-total-consumed"] = P1Property(
                                                        self.thing,
                                                        "kwh-total-consumed",
                                                        {
                                                            '@type': 'LevelProperty',
                                                            'label': "Total consumed",
                                                            'type': 'number',
                                                            'unit': 'kwh',
                                                            'readOnly': True,
                                                            'multipleOf':0.001,
                                                        },
                                                        consumed_total)
                            
                                        targetProperty = self.thing.find_property('kwh-total-consumed')
                            
                                    new_value = get_int_or_float(consumed_total)
                                    targetProperty.update(new_value)

                    if 'high' in kwh:
                        if 'produced' in kwh['high']:
                            if 'low' in kwh:
                                if 'produced' in kwh['low']:
                                    produced_total = get_int_or_float(kwh['high']['produced']) + get_int_or_float(kwh['low']['produced'])
                                    if self.DEBUG:
                                        print("total produced = " + str(produced_total))
                                    
                                    if self.previous_produced_total == None:
                                        self.previous_produced_total = produced_total
                                    
                                    targetProperty = self.thing.find_property('kwh-total-produced')
                                    if targetProperty == None:
                                        self.thing.properties["kwh-total-produced"] = P1Property(
                                                        self.thing,
                                                        "kwh-total-produced",
                                                        {
                                                            'label': "Total produced",
                                                            'type': 'number',
                                                            'unit': 'kwh',
                                                            'readOnly': True,
                                                            'multipleOf':0.001,
                                                        },
                                                        produced_total)
                            
                                        targetProperty = self.thing.find_property('kwh-total-produced')
                            
                                    new_value = get_int_or_float(produced_total)
                                    targetProperty.update(new_value)


                    
                    if 'current_consumed' in kwh:
                        targetProperty = self.thing.find_property('kwh-current-consumed')
                        if targetProperty == None:
                            self.thing.properties["kwh-current-consumed"] = P1Property(
                                                self.thing,
                                                "kwh-current-consumed",
                                                {
                                                    'label': "Current consumed",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                kwh['current_consumed'])
                            targetProperty = self.thing.find_property('kwh-current-consumed')
                                                
                        new_value = get_int_or_float(kwh['current_consumed'])
                        targetProperty.update(new_value)
                        
                        
                    if 'current_produced' in kwh:
                        targetProperty = self.thing.find_property('kwh-current-produced')
                        if targetProperty == None:
                            self.thing.properties["kwh-current-produced"] = P1Property(
                                                self.thing,
                                                "kwh-current-consumed",
                                                {
                                                    'label': "Current produced",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                kwh['current_consumed'])
                            targetProperty = self.thing.find_property('kwh-current-produced')
                                                
                        new_value = get_int_or_float(kwh['current_produced'])
                        targetProperty.update(new_value)
                    
                    
                    if 'tariff' in kwh:
                        targetProperty = self.thing.find_property('kwh-tariff')
                        if targetProperty == None:
                            self.thing.properties["kwh-tariff"] = P1Property(
                                                self.thing,
                                                "kwh-tariff",
                                                {
                                                    'label': "Tariff",
                                                    'type': 'integer',
                                                    'readOnly': True,
                                                    #'multipleOf':0.001,
                                                },
                                                kwh['tariff'])
                            targetProperty = self.thing.find_property('kwh-tariff')
                            
                        new_value = get_int_or_float(kwh['tariff'])
                        targetProperty.update(new_value)
                                
                        
                except Exception as ex:
                    if self.DEBUG:
                        print("Energy use update error: " + str(ex))
                
                
                
                
                
                
                
                
                #
                #  INSTANTANEOUS POWER
                #
                
                
                try:
                    instant = packet['instantaneous']
                    
                    instant_total_watts = 0
                    
                    if self.DEBUG:
                        print("--------INSTANTANEOUS---------")
    
                        for key, value in instant.items():
                            print(key, ' : ', value)
    
                        print("--------------------")
                    
                    if 'l1' in instant:
                        if 'watts' in instant['l1']:
                            targetProperty = self.thing.find_property('instant-l1-watts')
                            if targetProperty == None:
                                if self.DEBUG:
                                    print("-instant-l1-watts property did not exist yet. Creating it now.")
                                self.thing.properties["instant-l1-watts"] = P1Property(
                                                self.thing,
                                                "instant-l1-watts",
                                                {
                                                    'label': "L1 wattage",
                                                    'type': 'number',
                                                    'unit': 'Watt',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                instant['l1']['watts'])
                                targetProperty = self.thing.find_property('instant-l1-watts')
                                
                            new_value = get_int_or_float(instant['l1']['watts'])
                            targetProperty.update(new_value)
                            
                            instant_total_watts += new_value
                            
                    if 'l2' in instant:
                        if 'watts' in instant['l2']:
                            targetProperty = self.thing.find_property('instant-l2-watts')
                            if targetProperty == None:
                                if self.DEBUG:
                                    print("-instant-l2-watts property did not exist yet. Creating it now.")
                                self.thing.properties["instant-l2-watts"] = P1Property(
                                                self.thing,
                                                "instant-l2-watts",
                                                {
                                                    'label': "L2 wattage",
                                                    'type': 'number',
                                                    'unit': 'Watt',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                instant['l2']['watts'])
                                targetProperty = self.thing.find_property('instant-l2-watts')
                                
                            new_value = get_int_or_float(instant['l2']['watts'])
                            targetProperty.update(new_value)
                            
                            instant_total_watts += new_value
                     
                     
                    if 'l3' in instant:
                        if 'watts' in instant['l3']:
                            targetProperty = self.thing.find_property('instant-l3-watts')
                            if targetProperty == None:
                                if self.DEBUG:
                                    print("-instant-l3-watts property did not exist yet. Creating it now.")
                            self.thing.properties["instant-l3-watts"] = P1Property(
                                            self.thing,
                                            "instant-l3-watts",
                                            {
                                                'label': "L3 wattage",
                                                'type': 'number',
                                                'unit': 'Watt',
                                                'readOnly': True,
                                                'multipleOf':0.001,
                                            },
                                            instant['l3']['watts'])
                            targetProperty = self.thing.find_property('instant-l3-watts')

                            new_value = get_int_or_float(instant['l3']['watts'])
                            targetProperty.update(new_value)

                            instant_total_watts += new_value
                             
                             
                    if instant_total_watts != 0:
                        targetProperty = self.thing.find_property('instant-total-watts')
                        if targetProperty == None:
                            if self.DEBUG:
                                print("-instant-total-watts property did not exist yet. Creating it now.")
                            
                            self.thing._type.append('EnergyMonitor')   
                            self.thing.properties["instant-total-watts"] = P1Property(
                                            self.thing,
                                            "instant-total-watts",
                                            {
                                                '@type': 'InstantaneousPowerProperty',
                                                'label': "Wattage",
                                                'type': 'number',
                                                'unit': 'Watt',
                                                'readOnly': True,
                                                'multipleOf':0.001,
                                            },
                                            instant_total_watts)
                            targetProperty = self.thing.find_property('instant-total-watts')
                           
                        new_value = get_int_or_float(instant_total_watts)
                        targetProperty.update(instant_total_watts)
                             
                        
                except Exception as ex:
                    if self.DEBUG:
                        print("Instantaneous energy use update error (your device simply may not support this): " + str(ex))
                
                
                
                
                
                #
                #  GAS
                #
                
                try:
                    gas = packet['gas']
                    
                    if self.DEBUG:
                        print("--------GAS---------")
    
                        for key, value in gas.items():
                            print(key, ' : ', value)
    
                        print("---------------------")
                    
                    if 'total' in gas:
                        targetProperty = self.thing.find_property('gas-total')
                        if targetProperty == None:
                            if self.DEBUG:
                                print("gas property did not exist yet, creating it now")
                            self.thing.properties["gas-total"] = P1Property(
                                                self.thing,
                                                "gas-total",
                                                {
                                                    'label': "Gas total",
                                                    'type': 'number',
                                                    'unit': 'm3',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                gas['total'])
                            targetProperty = self.thing.find_property('gas-total')
                            #print("targetProperty gas is now: " + str(targetProperty))
                        
                        new_value = get_int_or_float(gas['total'])
                        gas_total = new_value
                        if self.previous_gas_total == None:
                            self.previous_gas_total = gas_total
                        
                        #print("new gas value: " + str(new_value))
                        targetProperty.update(new_value)
                    
                except Exception as ex:
                    if self.DEBUG:
                        print("Gas update error: " + str(ex))





                try:
                    if seconds_counter > 60:
                        seconds_counter = 0
                        minutes_counter += 1
                        #print("")
                        #print("MINUTE")
                        #print("")
                        #if self.DEBUG:
                
                                 
                    
                        if minutes_counter > 60: # every hour
                            minutes_counter = 0
                            #print("total consumed = " + str(consumed_total))
                    
                            consumed_delta = consumed_total - self.previous_consumed_total
                            self.previous_consumed = consumed_total
                    
                            produced_delta = produced_total - self.previous_produced_total
                            self.previous_produced_total = produced_total                    
                    
                            gas_delta = gas_total - self.previous_gas_total
                            self.previous_gas_total = gas_total
                    
                    
                            # Hourly KWH consumption
                            targetProperty = self.thing.find_property('kwh-hourly-consumed')
                            if targetProperty == None:
                                self.thing.properties["kwh-hourly-consumed"] = P1Property(
                                                self.thing,
                                                "kwh-hourly-consumed",
                                                {
                                                    'label': "Hourly consumption",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                consumed_delta)
            
                                targetProperty = self.thing.find_property('kwh-total-consumed')
            
                            targetProperty.update(consumed_delta)
                    
                            # Hourly KWH production
                            targetProperty = self.thing.find_property('kwh-hourly-produced')
                            if targetProperty == None:
                                self.thing.properties["kwh-hourly-produced"] = P1Property(
                                                self.thing,
                                                "kwh-hourly-produced",
                                                {
                                                    'label': "Hourly production",
                                                    'type': 'number',
                                                    'unit': 'kwh',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                produced_delta)
            
                                targetProperty = self.thing.find_property('kwh-total-consumed')
            
                            targetProperty.update(produced_delta)
                    
                            # Hourly GAS consumption
                            targetProperty = self.thing.find_property('gas-hourly')
                            if targetProperty == None:
                                self.thing.properties["gas-hourly"] = P1Property(
                                                self.thing,
                                                "gas-hourly",
                                                {
                                                    'label': "Hourly gas consumption",
                                                    'type': 'number',
                                                    'unit': 'm3',
                                                    'readOnly': True,
                                                    'multipleOf':0.001,
                                                },
                                                gas_delta)
            
                                targetProperty = self.thing.find_property('gas-hourly')
            
                            targetProperty.update(gas_delta)

                except Exception as ex:
                    if self.DEBUG:
                        print("Hourly values update error: " + str(ex))



                # If the amount of properties has increased, tell the Gateway about this.
                if property_counter_before != len(self.thing.properties):
                    self.handle_device_added(self.thing)

                if self.thing.connected == False:
                    self.thing.connected = True
                    self.thing.connected_notify(True)
          
            except Exception as ex:
                print("Error handling incoming data: " + str(ex))
                try:
                    self.thing.connected = False
                    self.thing.connected_notify(False)
                except Exception as ex:
                    print("Error updating connection status: " + str(ex))
                
                try:
                    if str(ex).startswith('read failed: device reports readiness'):
                        print("It's likely that the wrong USB port has been selected. Will attempt to switch.")
                        print("len(self.initial_serial_devices) = " + str(len(self.initial_serial_devices)))
                        print("self.initial_serial_devices = " + str(self.initial_serial_devices))
                        print("str(self.initial_serial_devices[0]['port_id']) = " + str(self.initial_serial_devices[0]))
                        
                        if len(self.initial_serial_devices) > 1 and self.usb_port == str(self.initial_serial_devices[0]):
                            self.usb_port = str(self.initial_serial_devices[1])
                        elif len(self.initial_serial_devices) > 2 and self.usb_port == str(self.initial_serial_devices[1]):
                            self.usb_port = str(self.initial_serial_devices[2])
                        elif len(self.initial_serial_devices) > 1 and self.usb_port == str(self.initial_serial_devices[1]):
                            self.usb_port = str(self.initial_serial_devices[0])
                            
                        print("Will try a new USB port: " + str(self.usb_port))
                        self.meter = SmartMeter(self.usb_port)
                        
                except Exception as ex:
                    print("Automatic switching to different USB port failed: " + str(ex))


                    

            time.sleep(1)
            seconds_counter += 1
            
        if self.DEBUG:
            print("While-loop in clock thread has been exited")




    def unload(self):
        print("Shutting down P1 adapter")
        self.running = False
        


    def remove_thing(self, device_id):
        if self.DEBUG:
            print("-----REMOVING:" + str(device_id))
        
        try:
            obj = self.get_device(device_id)        
            self.handle_device_removed(obj)                     # Remove from device dictionary
            print("Removed device")
        except:
            print("Could not remove things from devices")



    def scan_usb_ports(self): # Scans for USB serial devices
        if self.DEBUG:
            print("Scanning USB serial devices")
        #initial_serial_devices = set()
        #result = {"state":"stable","port_id":[]}
        self.initial_serial_devices = []
        
        try:    
            ports = prtlst.comports()
            if self.DEBUG:
                print("All serial ports: " + str(ports))
            for port in ports:
                if 'USB' in port[1]: #check 'USB' string in device description

                    if self.DEBUG:
                        print("adding possible port with 'USB' in name to list: " + str(port))
                    #if self.DEBUG:
                    #    print("port: " + str(port[0]))
                    #    print("usb device description: " + str(port[1]))
                    if str(port[0]) not in self.initial_serial_devices:
                        self.initial_serial_devices.append(str(port[0]))
                        
        except Exception as e:
            print("Error getting serial ports list: " + str(e))



    def add_from_config(self):
        """Attempt to add all configured devices."""
        try:
            database = Database('p1-adapter')
            if not database.open():
                return

            config = database.load_config()
            database.close()
        except:
            print("Error! Failed to open settings database.")
            return

        if not config:
            print("Error loading config from database")
            return
        
        
        
        # Debug
        try:
            if 'Debugging' in config:
                self.DEBUG = bool(config['Debugging'])
                if self.DEBUG:
                    print("Debugging is set to: " + str(self.DEBUG))
            else:
                self.DEBUG = False
        except:
            print("Error loading debugging preference")
            
        
        
        # USB port from dropdown
        try:
            if 'USB port' in config:
                if str(config['USB port']) == 'USB port 1':
                    self.usb_port = self.initial_serial_devices[0]
                if str(config['USB port']) == 'USB port 2':
                    self.usb_port = self.initial_serial_devices[1]
                if str(config['USB port']) == 'USB port 3':
                    self.usb_port = self.initial_serial_devices[2]
                if str(config['USB port']) == 'USB port 4':
                    self.usb_port = self.initial_serial_devices[3]         
        except Exception as ex:
            print("Error with USB port selection: " + str(ex))
    
            
        # Custom USB port command. Overrides dropdown selection.
        try:
            if 'Custom USB port command' in config:
                if str(config['Custom USB port command']) != "":
                    self.usb_override = True
                    self.usb_port = str(config['Custom USB port command'])
                else:
                    print("Custom USB port command was empty")

        except Exception as ex:
            print("Error setting custom USB port command:" + str(ex))
            
        print("selected USB port: " + str(self.usb_port))


#
#  DEVICE
#

class P1Device(Device):
    """P1 device type."""

    def __init__(self, adapter):
        """
        Initialize the object.
        adapter -- the Adapter managing this device
        """

        
        Device.__init__(self, adapter, 'p1-device')
        #print("Creating P1 thing")
        
        self._id = 'p1-device'
        self.id = 'p1-device'
        self.adapter = adapter
        self._type.append('MultiLevelSensor')

        self.name = 'p1-device'
        self.title = 'Energy sensor'
        self.description = 'P1 Energy use sensor'

        if self.adapter.DEBUG:
            print("Empty P1 thing has been created.")




#
#  PROPERTY
#


class P1Property(Property):
    """P1 property type."""

    def __init__(self, device, name, description, value):
        
        #print("incoming thing device at property init is: " + str(device))
        Property.__init__(self, device, name, description)
        
        
        self.device = device
        self.name = name
        self.title = name
        self.description = description # dictionary
        self.value = value
        self.set_cached_value(value)



    def set_value(self, value):
        #print("set_value is called on a P1 property. This should not be possible?")
        pass


    def update(self, value):
        #print("p1 property -> update to: " + str(value))
        #if value != self.value:
        self.value = value
        self.set_cached_value(value)
        self.device.notify_property_changed(self)


