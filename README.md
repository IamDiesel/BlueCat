# Tracker and homecoming alert for Kippy cat tracker #
<img width="2087" height="753" alt="image" src="https://github.com/user-attachments/assets/7cb2d305-d781-47d0-a527-649006ad3ae8" />


This project uses the web application of kippy cat tracker to extract the gps coordinates and send them to home assistant. Also a bluetooth scanner scans for the kippy cat tracker beacon and sends the rssi to home assistant.
Home assistant then triggers an alert when the tracker is within the home region.

# Used Hardware #
* Kippy CAT:  https://www.kippy.eu/de/product/kippy-cat
* Raspberry Pi 5 running Home Assistant Supervised
* UGREEN Bluetooth Adapter 5.3: https://www.amazon.de/UGREEN-Bluetooth-%C3%9Cbertragungsreichweite-Kopfh%C3%B6rer-Controller-Schwarz/dp/B0BXF13GB7




# Home Assistant automations and entities #
## Automations ##
### Update Device Tracker ###
<img width="1961" height="996" alt="image" src="https://github.com/user-attachments/assets/16be4739-6edb-420f-9a62-b8fdd62fc39a" />
<img width="1962" height="729" alt="image" src="https://github.com/user-attachments/assets/6769d41a-3581-47d2-945c-048a7330ce97" />

```
action: device_tracker.see
data:
  dev_id: lola_kippy_device_tracker
  gps:
    - "{{ states('input_text.bluecat_gps_longitude') | float | round(7) }}"
    - "{{ states('input_text.bluecat_gps_latitude') | float | round(7) }}"
  gps_accuracy: "{{ states('input_number.bluecat_radius')}}"
  battery: "{{ states('input_number.bluecat_battery_percentage')}}"
```
### Start Kippy Tracking ###

```
alias: bluecat_start_tracking_automation
description: ""
triggers:
  - trigger: state
    entity_id:
      - input_boolean.bluecat_start_gps_tracking
    to: "on"
conditions: []
actions:
  - action: input_boolean.turn_on
    metadata: {}
    data: {}
    target:
      entity_id: input_boolean.bluecat_start_gps_tracking_event
mode: single
```

### Stop Kippy Tracking ###
```
alias: bluecat_stop_tracking_automation
description: ""
triggers:
  - trigger: state
    entity_id:
      - input_boolean.bluecat_start_gps_tracking
    to: "off"
conditions: []
actions:
  - action: input_boolean.turn_on
    metadata: {}
    data: {}
    target:
      entity_id: input_boolean.bluecat_stop_gps_tracking_event
mode: single
```
### GPS Alarm ###
```
alias: Lola Homecoming Alert
description: ""
triggers:
  - trigger: zone
    entity_id: device_tracker.lola_kippy_device_tracker
    zone: zone.home
    event: enter
conditions:
  - condition: state
    entity_id: input_boolean.bluecat_kippy_gps_active
    state: "on"
actions:
  - device_id: yourIDNumber
    domain: mobile_app
    type: notify
    message: "[GPS] Lola is coming home "
    title: RedCat Alert
  - device_id: yourIDNumber
    domain: mobile_app
    type: notify
    message: "[GPS] Lola is coming home "
    title: "RedCat Alert "
  - action: notify.notify
    metadata: {}
    data:
      message: "[GPS] Lola is coming home "
      title: "RedCat Alert "
mode: single
```

### BT Alarm ###
```
alias: bluecat_homecoming_bt_only
description: ""
triggers:
  - trigger: numeric_state
    entity_id:
      - input_number.bluecat_received_signal_strength
    above: -105
conditions:
  - condition: state
    entity_id: input_boolean.bluecat_kippy_gps_active
    state: "on"
actions:
  - device_id: d15a62e25d48aff0da1ab21113af5a41
    domain: mobile_app
    type: notify
    message: "[BT] Lola is coming home"
    title: BlueCat Alert
  - device_id: 54e906bd82a1ad34e3eef09e5181c812
    domain: mobile_app
    type: notify
    message: "[BT] Lola is coming home"
    title: BlueCat Alert
  - action: notify.notify
    metadata: {}
    data:
      message: "[BT] Lola is coming home"
      title: BlueCat Alert
mode: single
```


## Helper ##
<img width="3515" height="1126" alt="image" src="https://github.com/user-attachments/assets/3aed14ff-f35c-421f-9d33-05538abd309b" />


## known_devices.yaml
<img width="788" height="325" alt="image" src="https://github.com/user-attachments/assets/5ea3edcf-b2be-43dd-af94-4469fea242e3" />


## /homeassistant/configuration.yaml
<img width="1815" height="214" alt="image" src="https://github.com/user-attachments/assets/71facd97-ea48-49ea-ab81-5d4e6999d165" />

## Image for tracker
Copy image to the following folders:
/usr/share/hassio/homeassistant/www
/usr/share/hassio/www



# Future features #
[ x ] Use bluetooth beacon of Kippy tracker as second validator for the cat returning home
