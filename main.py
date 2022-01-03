import datetime
import requests
import json
import pandas as pd
import numpy as np

from requests.api import get


class Cleaned_list:

    # Konstruktori
    def __init__(self, header: str, data: dict):
        self.header = header
        self.data = data

    def get_header(self):
        listed_data = {}
        list_val = []
        header_data = {key: value for(
            key, value) in self.data.items() if key == self.header}

        for i in header_data.values():
            for j in i:
                listed_data[j[1]] = pd.Timestamp((j[0]/1000), unit='s')

        list_val = list(listed_data.items())
        df = pd.DataFrame(data=list_val)
        df['new_date'] = pd.to_datetime(df[1], format='%d-%m-%y %H:%M')
        df['date'] = df['new_date'].dt.date
        dates = (df.set_index('date').groupby(
            level=0)[1].agg([('min', np.min)]))
        dates_list = dates['min'].values.tolist()

        for i in range(len(dates_list)):
            x = int(str(dates_list[i])[:10])
            dates_list[i] = pd.Timestamp(x, unit='s')

        self.data = {key: value for (key, value) in listed_data.items() if str(
            pd.Timestamp(value, unit='s'))[:15] in str(dates_list)}
        return self.data


class Analyze(Cleaned_list):

    def __init__(self, header: str, data: dict):
        super().__init__(header, data)

    def get_investment_days(self):
        datarows = self.data
        it = iter(datarows)
        y = 0
        max_count = 0
        count = 0
        x = 0
        h = next(it)
        min_day = ''
        max_day = ''
        for i in datarows.keys():
            if i < h:
                y = i
                h = i
                count += 1
            else:
                if count > max_count:
                    max_count = count
                count = 0
                h = i
            if y != 0:
                key_of_min = y
                min_day = datarows[key_of_min]
                days_to_analyze = {key: value for (
                    key, value) in datarows.items() if value > datarows[key_of_min]}

                for k, v in days_to_analyze.items():
                    if k > x:
                        x = k
                        
        print(f"Maximum amount of days bitcoin's price was decreasing: {max_count}")
        min_day = min_day.strftime('%d-%m-%y')
        max_day = datarows[x].strftime('%d-%m-%y') 
        if x<= y:
            print("There are no good days to trade on those days") 
        else:
            print("In case you have a time machine:")
            print(f"Buy bitcoin on {min_day}. Its value on that day was {y:.2f} eur")
            print(
                f"{max_day} is a good day to sell the bitcoins you bought on {min_day}. then their value is {x:.2f} eur")

    def get_max_volume(self):
        data = self.data
        max_volume = 0

        for k, v in data.items():
            if k > max_volume:
                max_volume = k
                day_of_max = data[max_volume]
   
        day_of_max = day_of_max.strftime('%d-%m-%y')
        print(
            f"The day when the trading volume was the highest is: {day_of_max}, when the volume was:{max_volume:.2f} eur")

        ''' 
      
            for key, value in i:
                if value == y:
                    avain = key
            gen = (j for j in i if j[1] < avain)

            for j in gen:
                if j[1] > x:
                    x = j[1]
                    max_day = j[0]/1000

            if x <= y:
                print("Dont buy or sell")
            else:
                max_day = datetime.datetime.fromtimestamp(max_day).strftime('%d-%m-%y')
                min_day = datetime.datetime.fromtimestamp(min_day).strftime('%d-%m-%y')
                print(f"Buy bitcoin on{min_day} Its value on that day was {y}")
                print(f"{max_day} is a good day to sell the bitcoins you bought on {min_day}. then their value is {x}")
'''


start_date = '01/07/2021'
end_date = '01/08/2021'
#start_date = input("Eneter the start date: ")
start = datetime.datetime.strptime(start_date, "%d/%m/%Y").timestamp()

#end_date = input("Enter the end date: ")
end = datetime.datetime.strptime(end_date, "%d/%m/%Y").timestamp()

r = r = requests.get(
    f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=eur&from={start}&to={end}").text

r = json.loads(r)

prices = Cleaned_list('prices', r)
prices.get_header()
invest_days = Analyze('prices', prices.data)
invest_days.get_investment_days()

volumes = Cleaned_list('total_volumes', r)
volumes.get_header()
max_volumes = Analyze('total_volumes', volumes.data)
max_volumes.get_max_volume()
