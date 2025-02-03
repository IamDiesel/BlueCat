import requests
import time
from homeassistant_api import Client, State, errors
from HASS_Token import token, kippy_pass, kippy_mail

class Kippy_http_handler():
    def __init__(self, mail, pw, hw_id,persistant_HASS_token):
        self.mail = mail
        self.pw = pw
        self.hw_id = hw_id
        self.csrf = self.get_csrf()
        self.hass_helper = self.HASS_Helper(persistant_HASS_token)
        
    def get_url(self, url):
        #url = 'http://www.google.de'
        r = requests.get(url)
        #print("Code:"+str(r.status_code))
        #print(r.headers)
        #print(r.content)  # bytes
        #print(r.text)     # r.content as str
        if r.status_code == 200:
            return r.text
        else: return None
    
    def get_csrf(self):
        url = 'https://webapp.kippy.eu/de/map/'+ self.hw_id
        res = self.get_url(url)
        if res is not None:
            print(res.split('meta name="csrf-token" content="')[1].split('==">')[0])
        else:
            return None
        
    def login(self,csrf):
        url = "https://webapp.kippy.eu/de/login"
        data ={'_csrf':csrf, 'LoginForm[username]':self.mail, 'LoginForm[password]':self.pw, 'login-button':''}
        r = requests.post(url=url, data=data)
        return r.text
        #print(r.text)
        #self.get_pos(r.text)
    def get_pos_from_server(self):
        html = self.login(self.csrf)
        return self.get_pos(html)
    
    def get_pos(self,html_body):
        part = html_body.split('var petlat = ')[1]
        latitude = part.split(';')[0]
        longitude = part.split('= ')[1].split(';')[0]
        #print(f'Longitude: [{latitude}]')
        #print(f'Longitude: [{longitude}]')
        return latitude, longitude
    
    def get_pos_after_login(self):
        url = 'https://webapp.kippy.eu/de/map/'+ self.hw_id
        res = self.get_url(url)
        if res is not None:
            return self.get_pos(res)
        else:
            return None
    def run(self):
        while(True):
            activate_tracking = self.hass_helper.get_entity_state('input_boolean.bluecat_kippy_gps_active')
            time.sleep(1)
            if(activate_tracking == 'on'):
                longitude, latitude = kip.get_pos_from_server()
                print(f'Latitude: [{latitude}]')
                self.hass_helper.set_entity_state('input_text.bluecat_gps_longitude',longitude)
                self.hass_helper.set_entity_state('input_text.bluecat_gps_latitude',latitude)
                print(f'Longitude: [{longitude}]')
                time.sleep(10)
        
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
            client = Client(self.URL, self.persistant_HASS_token)
            client.set_state(State(state=value, entity_id=entity_id))
            
        def get_entity_state(self, entity_id):
            client = Client(self.URL, self.persistant_HASS_token) 
            entity = client.get_entity(entity_id=entity_id) #session is closed after this call
            return entity.get_state().state
        
        
if __name__ == '__main__':
    hw_id = "AD2NXL3"
    kip = Kippy_http_handler(kippy_mail,kippy_pass, hw_id, token)
    #url = 'http://www.google.de'
    kip.run()

    
