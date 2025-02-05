# Tracker and homecoming alert for Kippy cat tracker #
![image](https://github.com/user-attachments/assets/43e087ed-13bc-4841-8f9e-64b9fd3cd7c9)
![image](https://github.com/user-attachments/assets/c7574526-b255-4e1c-ac80-555104cfaaf5)

This project uses the web application of kippy cat tracker to extract the gps coordinates and send them to home assistant. Also a bt scanner scans for the kippy cat tracker beacon and sends the rssi to home assistant.
Home assistant then triggers an alert when the tracker is within the home region.




# Home Assistant automations and entities #
## Automations ##
![image](https://github.com/user-attachments/assets/31d8f504-0fbe-401b-9317-d1d026aa9b16)
![image](https://github.com/user-attachments/assets/4fd31ce9-44d7-4525-ba2f-554447de04ca)
## Helper ##
![image](https://github.com/user-attachments/assets/e97cea9e-a2b1-419a-bfd8-07ce6f3ff0c8)

## know_devices.yaml
![image](https://github.com/user-attachments/assets/c2c9431a-b42c-4f22-8a99-9ee5ea748763)


# Future features #
[ x ] Use bluetooth beacon of Kippy tracker as second validator for the cat returning home
