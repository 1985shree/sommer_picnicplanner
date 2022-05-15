from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import pandas as pd
import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def index():
     return {"Greetings": "welcome to the picnic planning app"}


@app.get("/predict_picnic")
def predict_picnic(date_from,
            date_to, place1, place2, place3, place4):

    weather_params = {"key": ["2013-07-06 17:18:00"],
                    "date_from" : date_from,
                    "date_to": date_to,
                    "place1": place1,
                    "place2": place2,
                    "place3": place3,
                    "place4": place4,
                    }
    weather_dict = []


    #create a list of dates:

    start_date_dt = datetime.strptime(weather_params['date_from'], "%Y-%m-%d")
    end_date_dt = datetime.strptime(weather_params['date_to'], "%Y-%m-%d")


    delta = end_date_dt - start_date_dt  # returns timedelta


    day_list = []
    for i in range(delta.days + 1):
        day = (start_date_dt + timedelta(days=i)).date()
        day = day.strftime("%Y-%m-%d")

        day_list.append(day)

    for day in day_list:
        places = [weather_params['place1'], weather_params['place2'], weather_params['place3'], weather_params['place4']]
        for loc in places:



            # #create a script to find latitude and longitude:
            geolocator = Nominatim(user_agent="shree_app")


            location = geolocator.geocode(loc)
            latitude = location.latitude
            longitude = location.longitude


            # #make url

            url = f"https://api.brightsky.dev/weather?lat={latitude}&lon={longitude}&date={day}"

            #print(url)
            r = requests.get(url).json()
            weather = r['weather']
            n = len(weather)
            avg_windspeed = np.mean([wind['wind_speed'] for wind in weather if wind['wind_speed'] != None])
            avg_temperature = np.mean([temp['temperature'] for temp in weather if temp['temperature'] != None])
            avg_sunshine = np.mean([sun['sunshine'] for sun in weather if sun['sunshine'] != None])
            avg_precipitation = np.mean([prec['precipitation'] for prec in weather if prec['precipitation'] != None])
            weather_dict.append({'date': day,
                                 'location': loc,
                                        'avg_windspeed': avg_windspeed,
                                        'avg_temperature' : avg_temperature,
                                        'avg_sunshine' : avg_sunshine,
                                        'avg_precipitation' : avg_precipitation})

            df = pd.DataFrame.from_dict(weather_dict)
            df_fill = df.fillna(0)

            df_new = df_fill[(df_fill['avg_windspeed']<= 30.0) &
            (df_fill['avg_temperature']<= 30.0) &
            (df_fill['avg_temperature']>= 20.0) &
            (df_fill['avg_sunshine']>= 20.0) &
            (df_fill['avg_precipitation']<= 0.05)]

            df_result = df_new[['date','location']]



    return {'picnic planner' : df_result}
