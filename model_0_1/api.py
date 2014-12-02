import datetime as dt
import numpy as np
import pandas as pd
import os
import sys
from collections import deque

# Historic temperatures from http://www.intellicast.com/Local/History.aspx?location=USNY0996
hist_avg_low_temp = {
    1:23, 2:24, 3:32,
    4:42, 5:53, 6:63,
    7:68, 8:66, 9:58,
    10:47, 11:38, 12:28,
}

class CitibikeForecaster:
  def __init__(self):
    d = pd.read_csv(os.path.join(os.path.dirname(__file__), "metadata.txt"))
    d = d[d.n_obs > 500000] # Remove the stations with too little data
    d = d.filter(regex="station_name|type|p_*")

    self.d = d
    self.dp = d.pivot("station_name", "type")

  # time in UTC seconds unixtime
  def forecast(self, station_name, current_num_bikes, current_time, until_time):
    station_metadata = self.d[self.d.station_name == station_name]
    arrivals_beta = station_metadata[station_metadata.type == "arrivals"]\
        .filter(regex="p_*").as_matrix()[0][1:]
    departures_beta = station_metadata[station_metadata.type == "departures"]\
        .filter(regex="p_*").as_matrix()[0][1:]
    current_dt = pd.to_datetime(current_time*1e9).tz_localize("UTC")
    until_dt = pd.to_datetime(until_time*1e9).tz_localize("UTC")

    forecasts = deque([(current_time, current_num_bikes)])
    while current_dt < until_dt:
      current_dt += dt.timedelta(seconds=60)
      current_dt_nyc = current_dt.tz_convert("US/Eastern")

      x_hour = [0.0] * 24
      x_hour[current_dt_nyc.hour] = 1.0
      x_hour = x_hour[1:]

      x_day_of_week = [0.0] * 7
      x_day_of_week[current_dt_nyc.weekday()] = 1.0
      x_day_of_week = x_day_of_week[1:]

      x_hist_avg_low_temp = hist_avg_low_temp[current_dt_nyc.month]
      x_hist_avg_low_temp_sqr = x_hist_avg_low_temp * x_hist_avg_low_temp

      
      x = np.array([1.0] + x_hour + x_day_of_week + [x_hist_avg_low_temp, x_hist_avg_low_temp_sqr])

      predicted_delta_bikes = np.exp(np.dot(x, arrivals_beta)) - np.exp(np.dot(x, departures_beta))
      current_num_bikes += predicted_delta_bikes

      forecasts.append( (int(current_dt.strftime("%s")), current_num_bikes) )

    return list(forecasts)

if __name__ == "__main__":
  cf = CitibikeForecaster()
  forecasts = cf.forecast("1-Ave-and-E-15-St", 10, 1417385370, 1417389000)
  print "\n".join(map(lambda x: str(x), forecasts))
