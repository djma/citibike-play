import os
from flask import Flask
from model_0_1 import api

app = Flask(__name__)
cf = api.CitibikeForecaster()

@app.route("/")
def hello():
    return "<a href='predict/1-Ave-and-E-15-St/10/1417385370/1417389000'>Hello</a>"

@app.route("/predict/<station>/<int:num_bikes>/<int:start_time>/<int:end_time>")
def predict(station, num_bikes, start_time, end_time):
    forecasts = cf.forecast(station, num_bikes, start_time, end_time)
    return "\n".join(map(lambda x: str(x), forecasts))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
