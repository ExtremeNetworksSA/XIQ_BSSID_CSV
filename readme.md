# XIQ BSSID CSV
## XIQ_bssid_csv.py
### Purpose
This script will leverage ExtremeCloudIQ's API to send the 'show interface' cli command to mulitple APs. The output is then parsed using a textfsm template. From this parsed data a CSV is created with the AP, interface, bssid, and ssid information. 

## Information
### Needed files

The XIQ_bssid_csv.py script uses several other files. If these files are missing the script will not function.
In the same folder as the XIQ_bssid_csv.py script there should be an /app/ folder. Inside of this folder should be a bssid_logger.py and xiq_api.py scripts. After running the script a new file 'XIQ_bssid_csv.log' will be created.

## Running the script

When running the script a prompt will display asking for a file with a list of devices. This should just be a .txt file with a list of device host names you would like to gather the BSSIDs for.
Once you have entered a file name the script will ask for your XIQ login credentials.

### flags
There is an optional flag that can be added when the script is ran.
```
--external
```
This flag will allow you to collect bssids on an XIQ account you are an external user on. After logging in with your XIQ credentials the script will give you a numeric option of each of the XIQ instances you have access to. Choose the one you would like to use.
```

## requirements
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.