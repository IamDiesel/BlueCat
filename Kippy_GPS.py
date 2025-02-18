import time
from homeassistant_api import Client, State, errors
from threading import Thread
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import datetime
import shutil
#import requests
#import re

class Kippy_http_handler(Thread):
    def __init__(self, mail, pw, hw_id, persistant_HASS_token):
        """
        mail: Kippy Account mailadress/username
        pw: Kippy Account password
        hw_id: Serialnumber of kippy device (cat tracker)
        persistant_HASS_token: home assistant long token (can be generated in Home Assistant settings)
        """
        self.mail = mail
        self.pw = pw
        self.hw_id = hw_id
        #self.csrf = self.get_csrf()
        self.hass_helper = self.HASS_Helper(persistant_HASS_token)
        self.running = False
        self.last_update = None
        self.tracking_active = False
        display = Display(visible=0, size=(1600, 1200))
        display.start()
        options = webdriver.ChromeOptions()
        chromedriver_path = shutil.which("chromedriver")
        service = webdriver.ChromeService(executable_path=chromedriver_path)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=service, options=options)
        super(Kippy_http_handler, self).__init__()
        print("finished initializing GPS")

    def activate_tracking(self):
        status_green = self.driver.execute_script("""return $('#live_btn').hasClass('status_green');""")
        status_yellow = self.driver.execute_script("""return $('#live_btn').hasClass('status_yellow');""")
        if (status_green == False and status_yellow == False):
            print("activating tracking")
            self.driver.execute_script("""return $('#live_btn').click();""")
            time.sleep(5)
        else:
            print(f"can't acivate tracking because of live button status: status_green:{status_green}, status_yellow:{status_yellow}")

    def deactivate_tracking(self):
        status_green = self.driver.execute_script("""return $('#live_btn').hasClass('status_green');""")
        if (status_green == True):
            print("deactivating tracking")
            self.driver.execute_script("""return $('#live_btn').click();""")
            time.sleep(5)

    def get_timestamp_last_update(self):
        lastupdate_seconds = self.driver.execute_script("""return secondiagg;""")
        timestamp = datetime.datetime.now() - datetime.timedelta(seconds=lastupdate_seconds)
        #print(timestamp)
        return timestamp
    
    def alternate_current_last_update(self, count):
        if(count % 2 == 0):
            return self.last_update - datetime.timedelta(microseconds=1)
        else:
            return self.last_update + datetime.timedelta(microseconds=1)

    def login(self):
        self.driver.get('https://webapp.kippy.eu/de/login')
        time.sleep(1)
        try:
            txt_user = self.driver.find_element(By.ID,"loginform-username")
            txt_pw = self.driver.find_element(By.ID,"loginform-password")
            txt_user.send_keys(self.mail)
            txt_pw.send_keys(self.pw)
            login_button = self.driver.find_element(By.NAME,"login-button")
            login_button.click()
            time.sleep(5)
        except NoSuchElementException:
            pass #still logged in

    def get_value_from_live_button_status(self, status_green, status_grey, status_yellow):
        if(status_green):
            return '3'
        elif(status_grey):
            return '2'
        elif(status_yellow):
            return '1'
        else:
            return '0' #error
        

    def run(self):
        self.running = True
        #https://www.qatouch.com/blog/selenium-with-python-tutorial/
        #https://patrikmojzis.medium.com/how-to-run-selenium-using-python-on-raspberry-pi-d3fe058f011
        # https://stackoverflow.com/questions/40735442/how-to-return-value-from-javascript-using-selenium
        reload_site_seconds = 350#350
        self.login()
        update_interval_seconds = 1
        time_count = 0
        #start_live_tracking = False
        tracking_stop_sequence = False
        while(self.running):
            try:
                time.sleep(update_interval_seconds)
                time_count += update_interval_seconds

                #TODO Tick home assistant via helper in order to update last timestamp value inside homeassistant
                #check for user interaction
                user_start_gps = self.hass_helper.get_entity_state('input_boolean.bluecat_start_gps_tracking_event')
                user_stop_gps = self.hass_helper.get_entity_state('input_boolean.bluecat_stop_gps_tracking_event')
                
                #Read kippy data and forward to home assistant
                if(self.tracking_active == True or user_start_gps == 'on' or user_stop_gps == "on" or tracking_stop_sequence):                
                    print("update")
                    if(time_count % reload_site_seconds == 0):
                        self.login()
                        print(f"Bat:{battery_percentage},Lat:{petlat},Lon:{petlon},Rad:{radius},status_green:{status_green},lastupdate:{last_update}")
                    activate_aquisition = self.hass_helper.get_entity_state('input_boolean.bluecat_kippy_gps_active')
                    
                    #self.activate_tracking()
                    #read latitude, radius, live-button-status, battery and last update
                    petlat = self.driver.execute_script("""return window.markerpet.getPosition().lat();""")
                    petlon = self.driver.execute_script("""return window.markerpet.getPosition().lng();""")
                    radius = self.driver.execute_script("""return window.petCircle.getRadius();""")
                    status_green = self.driver.execute_script("""return $('#live_btn').hasClass('status_green');""")
                    status_grey = self.driver.execute_script("""return $('#live_btn').hasClass('status_grey');""")
                    status_yellow = self.driver.execute_script("""return $('#live_btn').hasClass('status_yellow');""")
                    battery_percentage = self.driver.find_element(By.CLASS_NAME, "battery").text.replace('%','')
                    self.last_update = self.get_timestamp_last_update()
                    
                    #submit values to home assistant
                    self.hass_helper.set_entity_state('input_text.bluecat_gps_longitude', str(petlat))
                    self.hass_helper.set_entity_state('input_text.bluecat_gps_latitude', str(petlon))
                    self.hass_helper.set_entity_state('input_number.bluecat_battery_percentage', str(battery_percentage))
                    self.hass_helper.set_entity_state('input_text.bluecat_last_update', str(self.last_update))
                    self.hass_helper.set_entity_state('input_number.bluecat_status_live_button',str(self.get_value_from_live_button_status(status_green,status_grey,status_yellow)))
                    self.hass_helper.set_entity_state('input_number.bluecat_radius', str(radius))
                    
                    if(tracking_stop_sequence):
                        if(status_grey is True):
                            tracking_stop_sequence = False
                elif(self.last_update is not None):
                    self.hass_helper.set_entity_state('input_text.bluecat_last_update', str(self.alternate_current_last_update(time_count)))
                    print("no update")
                    

                #execute user action
                if(user_start_gps == 'on'):
                    self.activate_tracking()
                    self.hass_helper.set_entity_state('input_boolean.bluecat_start_gps_tracking_event','off')
                    self.tracking_active = True
                elif(user_stop_gps == 'on'):
                    self.deactivate_tracking()
                    self.hass_helper.set_entity_state('input_boolean.bluecat_stop_gps_tracking_event', 'off')
                    self.tracking_active = False
                    tracking_stop_sequence = True
            except BaseException as e:
                print(e)
                self.hass_helper.set_entity_state('input_text.bluecat_last_update', 'Error at Kippy_GPS run')
                continue

        
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
    from BlueCat_ID import kippy_mail,kippy_pass, hw_id
    from HASS_Token import token
    kip = Kippy_http_handler(kippy_mail,kippy_pass, hw_id, token)
    kip_thread = Thread(target = kip.run)
    kip_thread.start()
    kip_thread.join()
    #url = 'http://www.google.de'
    #kip.login('asd')
    #kip.get_ajax_mapaction()
    #kip.run()

    
