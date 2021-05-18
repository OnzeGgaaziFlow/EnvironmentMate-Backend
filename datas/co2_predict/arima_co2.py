import tensorflow as tf
print(tf.__version__)
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
from datetime import datetime, timedelta

def plot_series(time, series, format="-", start=0, end=None):
    plt.plot(time[start:end], series[start:end], format)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.grid(True)

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[1:]))
    print(ds)
    return ds.batch(batch_size).prefetch(1)

def model_forecast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(4).prefetch(1)
    forecast = model.predict(ds)
    return forecast
import csv
times = []
temps = []

model_series_seasonal = tf.keras.models.load_model('./model/model_series_seasonal.h5')
model_series_resid = tf.keras.models.load_model('./model/model_series_resid.h5')
model_series_trend = tf.keras.models.load_model('./model/model_series_trend.h5')
#
# for i in range(48):

def predict():
    plt.switch_backend("Agg")
    with open('./data/CLM_온실가스_MNH_20210515164253.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        year = 1999
        month = 1
        for row in reader:
            temps.append(float(row[3]))
            times.append(datetime(year, month, 1))
            month += 1
            if month == 12:
                year += 1
                month = 1

        csv_co2 = np.array(temps)
        csv_times = np.array(times)
        predict_time = []
        result = []

        series_decompose = seasonal_decompose(csv_co2, model='additive', period=13, )
        series_resid = np.nan_to_num(series_decompose.resid, copy=False)
        series_trend = np.nan_to_num(series_decompose.trend, copy=False)
        series_seasonal = np.nan_to_num(series_decompose.seasonal, copy=False)
        series_trend_m = np.array(series_decompose.trend[-11:-6])
        series_resid_m = np.array(series_decompose.resid[-11:-6])
        series_seasonal_m = np.array(series_decompose.seasonal[-11:-6])
        month = month-6
        for i in range(48):
            series_trend_m = series_trend_m[-5:]
            series_seasonal_m = series_seasonal_m[-5:]
            series_resid_m = series_resid_m[-5:]
            window_size = 5
            rnn_forecast_s = model_forecast(model_series_seasonal, series_seasonal_m[..., np.newaxis], window_size)[-1][-1]
            rnn_forecast_r = model_forecast(model_series_resid, series_resid_m[..., np.newaxis], window_size)[-1][-1]
            rnn_forecast_t = model_forecast(model_series_trend, series_trend_m[..., np.newaxis], window_size)[-1][-1]
            result.extend(rnn_forecast_r + rnn_forecast_s + rnn_forecast_t)
            series_resid_m = np.append(series_resid_m, np.array(rnn_forecast_r))
            series_seasonal_m = np.append(series_seasonal_m, np.array(rnn_forecast_s))
            series_trend_m = np.append(series_trend_m, np.array(rnn_forecast_t))
            month += 1
            predict_time.append(datetime(year, month, 1))
            if month == 12:
                year += 1
                month = 1

        plt.figure(figsize=(10, 6))
        plot_series(csv_times, csv_co2)
        plot_series(predict_time, result)
        plt.title('Korea Greenhouse Gas Emissions Forecast')
        plt.xlabel('Times')
        plt.ylabel('CO2')
        plt.savefig('co2_kr.png')
    return

#%%
#############
#   TEST    #
#############
predict()