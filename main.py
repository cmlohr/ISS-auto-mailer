import requests
from datetime import datetime
import pytz
import smtplib
import time

# CONSTS (Currently Set to: New Orleans/CST)
LAT = 29.951065 #personal latitude
LNG = -90.071533 #personal longitude
# personal parameters removed before push to repo
FROM_EMAIL = "email0@mail.com" # account email sent from
PASSWORD = "XXXXXXXXXXXXXX" # account password
GMAIL_SMTP = "smtp.gmail.com" # set to google server
EMAIL = "email@mail.com" # email to get msg
PORT = "587"
TZ = pytz.timezone('US/Central') # set to central time zone

def is_overhead():
    # ISS API
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    longitude = float(data["iss_position"]["longitude"])
    latitude = float(data["iss_position"]["latitude"])

    # CONDITION
    if LAT - 5 <= latitude <= LAT + 5 and LNG - 5 <= latitude <= LNG + 5:
        return True


def is_night():
    location = {
        "lat": LAT,
        "lng": LNG,
        "formatted": 0,
    }
    current_hour = datetime.now().hour # gets current hour

    #SUNRISE/SUNSET API
    response = requests.get(url="https://api.sunrise-sunset.org/json", params=location)
    response.raise_for_status()
    sun_position = response.json()

    # SUNRISE & SUNSET DATA
    rise = sun_position["results"]["sunrise"]
    sun_set = sun_position["results"]["sunset"]

    # CONVERTS UTC JSON TO CST AND FORMATS TO THE HOUR
    utc_rise = datetime.strptime(rise, "%Y-%m-%dT%H:%M:%S%z")
    sunrise_hour = str(utc_rise.astimezone(TZ)).split(":")[0].split(" ")[1]
    utc_set = datetime.strptime(sun_set, "%Y-%m-%dT%H:%M:%S%z")
    sunset_hour = str(utc_set.astimezone(TZ)).split(":")[0].split(" ")[1]

    sunrise = int(sunrise_hour)
    sunset = int(sunset_hour)

    # CONDITION
    if current_hour >= sunset or current_hour <= sunrise:
        return True

# Looping program, checks every 60 seconds for ISS location.
while True:
    time.sleep(60) # program delay
    if is_overhead() and is_night():
        with smtplib.SMTP(GMAIL_SMTP, port=PORT) as connect:
            connect.starttls()
            connect.login(user=FROM_EMAIL, password=PASSWORD)
            connect.sendmail(
                from_addr=FROM_EMAIL,
                to_addrs=EMAIL,
                msg="Subject: The ISS is above you!\n\nLOOK UP!"
            )

