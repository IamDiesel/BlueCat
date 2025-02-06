import subprocess
import bluepy
from bluepy.btle import Scanner, DefaultDelegate
from threading import Thread
from homeassistant_api import Client, State, errors
import time
from datetime import datetime, timedelta

class BeaconDelegate(Thread, DefaultDelegate):
    def __init__(self, bt_addr_beacon, bt_addr_device, persistant_HASS_token):
        DefaultDelegate.__init__(self)
        self.bt_addr_beacon = bt_addr_beacon
        self.bt_addr_device = bt_addr_device
        self.bt_dev = self.getBTDeviceByBTAddress()
        self.scanner = Scanner(iface=int(self.bt_dev)).withDelegate(self)
        self.running = False
        super(BeaconDelegate, self).__init__()
        self.hass_helper = self.HASS_Helper(persistant_HASS_token)
        self.bluecat_rssi = -130 #-130 dB --> No signal
        self.count_findings = 0
        #self.beacon_found_flag = False
        self.timestamp_beacon_found = time.time()
        
        
    def run(self):
        self.running = True
        while(self.running):
            try:
                self.scanner.scan(10.0, passive=True)
                if((time.time() - self.timestamp_beacon_found) >= 10):
                    self.bluecat_rssi = '-130' #130db -> No signal
                    self.hass_helper.set_entity_state('input_number.bluecat_received_signal_strength', self.bluecat_rssi)
            except Exception as e:
                print(e," - error in Beacon Delegate run()")
                pass
            
        
    def getBTDeviceByBTAddress(self):
        device = None
        command = f'hciconfig | grep -B1 {self.bt_addr_device} | cut -c 4-4 | head -n 1'

        try:
            device = subprocess.check_output(command, shell = True, executable = "/bin/bash", stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            result = cpe.output
            print("Error@ScanDelecate: BT-Device not found on this system",result)
            pass           
        return device

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if(dev.addr == self.bt_addr_beacon):
            self.bluecat_rssi = str(dev.rssi)
            print(dev.rssi)
            self.hass_helper.set_entity_state('input_number.bluecat_received_signal_strength', self.bluecat_rssi)
            #self.beacon_found_flag = True
            self.timestamp_beacon_found = time.time()#datetime.now()
                
            
            
    class HASS_Helper:
        #helper for i/o from and to homeassistant
        def __init__(self, persistant_HASS_token):
            self.persistant_HASS_token = persistant_HASS_token
            self.URL = "http://localhost:8123/api"
            self.wait_for_api()
            
        def wait_for_api(self):
            exception_thrown = True
            while(exception_thrown):
                try:
                    self.get_entity_state("binary_sensor.rpi_power_status")
                    exception_thrown = False
                    time.sleep(15)
                except errors.EndpointNotFoundError:
                    time.sleep(15)
                    print("Waiting for API")
                    continue
                except Exception:
                    time.sleep(15)
                    print("Waiting for API")
                    continue
        
        def set_entity_state(self,entity_id, value):
            try:
                client = Client(self.URL, self.persistant_HASS_token)
                client.set_state(State(state=value, entity_id=entity_id))
            except ConnectionError as e:
                print("Connection error: could not set entity: error at Hass Helper:",e)
                time.sleep(5)
                pass
            except Exception as e:
                print("could not set entity: error at Hass Helper:",e)
                time.sleep(5)
                pass
            
        def get_entity_state(self, entity_id):
            try:
                client = Client(self.URL, self.persistant_HASS_token) 
                entity = client.get_entity(entity_id=entity_id) #session is closed after this call
                return entity.get_state().state
            except ConnectionError as e:
                print("Connection error: could not set entity: error at Hass Helper:",e)
                time.sleep(5)
                pass
            except Exception as e:
                print("could not set entity: error at Hass Helper:",e)
                time.sleep(5)
                pass

if __name__ == '__main__':
    from HASS_Token import token
    from BlueCat_ID import bt_addr_beacon, bt_addr_device
    scan_slave = BeaconDelegate(bt_addr_beacon=bt_addr_beacon,bt_addr_device=bt_addr_device, persistant_HASS_token=token)
    scan_slave_thread = Thread(target = scan_slave.run)
    scan_slave_thread.start()
    scan_slave_thread.join()
    

