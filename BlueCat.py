import Kippy_BT
import Kippy_GPS
from BlueCat_ID import bt_addr_beacon, bt_addr_device, hw_id, kippy_pass, kippy_mail
from HASS_Token import token
from threading import Thread

if __name__ == '__main__':

    cat_bt_scanner = Kippy_BT.BeaconDelegate(bt_addr_beacon=bt_addr_beacon,bt_addr_device=bt_addr_device,persistant_HASS_token=token)
    cat_bt_scanner_thread = Thread(target = cat_bt_scanner.run)
    cat_gps_scanner = Kippy_GPS.Kippy_http_handler(kippy_mail,kippy_pass, hw_id, token)
    cat_gps_scanner_thread = Thread(target = cat_gps_scanner.run)
    
    cat_bt_scanner_thread.start()
    cat_gps_scanner_thread.start()
    cat_gps_scanner_thread.join()
    cat_bt_scanner_thread.join()
