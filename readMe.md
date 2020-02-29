## Crowd Sorting

Crowd Sorting is a web application built by Matthew Cheney for the Department of Digital Humanities at Brigham Young University.

## Installing Crowd Sorting

Clone this repository to your machine or server</br>
Add admin emails to crowdsorting/app_resources/admins.txt</br>
pip install -r requirements.txt
NOTE - After installing flask-cas, you have to manually update the routing.py file. Comment out line 125, and enter this just below: attributes = xml_from_dict.get("cas:attributes", {})
Run: python3 initialize_databases.py
Run: python3 run.py

## Google oauth2

In order to authenticate with Google, you have to set up an app via the google developers dashboard. Once you have done so, set the following environment variables:
GOOGLE_CLIENT_ID='<id>'
GOOGLE_CLIENT_SECRET='<secret>'
