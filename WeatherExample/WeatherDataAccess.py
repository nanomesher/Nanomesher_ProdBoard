import sqlite3
import json


def InsertWeatherData(Temperature, Humidity, Pressure, CO2, Tvoc):
    conn = sqlite3.connect('../database/weather.db')
    curs = conn.cursor()
    curs.execute("PRAGMA synchronous=OFF")
    curs.execute("insert into WeatherData(Temperature, Humidity, Pressure, CO2, Tvoc, Time) values(?,?,?,?,?,datetime('now'))", [Temperature, Humidity, Pressure, CO2, Tvoc])
    newraceid = None

    conn.commit()
    conn.close()

InsertWeatherData(24, 71, 1050, 540, 30)



