import datetime
import requests
import json
import pandas as pd
import numpy as np

class Cleaned_list:


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
            dates_list[i] = pd.Timestamp(x, tz='US/Pacific',unit='s')

        self.data = {key: value for (key, value) in listed_data.items() if str(
            pd.Timestamp(value, tz='US/Pacific', unit='s'))[:15] in str(dates_list)}
        #print(self.data)
        return self.data
        


class Analyze(Cleaned_list):

    def __init__(self, header: str, data: dict):
        super().__init__(header, data)

    def get_investment_days(self):
        datarows = self.data
        print(datarows)
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
            
            if count > max_count:
                    max_count = count
                    count = 0
            h = i
            if  i == list(datarows.keys())[-1]:
                key_of_min = y
                min_day = datarows[key_of_min]
                days_to_analyze = {key: value for (
                    key, value) in datarows.items() if value > min_day}
                print(days_to_analyze)
                for k, v in days_to_analyze.items():
                    if k > x:
                        x = k
                        
        print(f"Maximum amount of days bitcoin's price was decreasing: {max_count}")
        min_day = min_day.strftime('%d-%m-%y')
        
        if x<= y:
            print("There are no good days to trade on those days") 
        else:
            max_day = datarows[x].strftime('%d-%m-%y') 
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
    
    def get_max_prof(self):
        data = list(self.data.keys())
        if len(data) == 0:
            return 0
        else:
            max_prof = 0
            min_price = data[0]
            max_price = data[0]
            key_of_min = 0
            key_of_max = 0

            for i in range(len(data)):
                profit= data[i]-min_price
                if profit > max_prof:

                    key_of_max = data[i]
                    key_of_min = min_price
                       
                max_prof = max(profit, max_prof)
                min_price = min(min_price, data[i])
                max_price = max(max_price, data[i])
            print(f"Buy bitcoin on {self.data[key_of_min].strftime('%d-%m-%y')}, Its value on that day was:{key_of_min:.2f} eur.")
            print(f"{self.data[key_of_max].strftime('%d-%m-%y')} is a good day to sell the bitcoins you bought, then their value is {key_of_max:.2f} eur. With one bitcoin you would earn {max_prof:.2f} eur")
            return max_prof





start_date = '06/01/2022'
end_date = '12/01/2022'
#start_date = input("Eneter the start date: ")
start = datetime.datetime.strptime(start_date, "%d/%m/%Y").timestamp()

#end_date = input("Enter the end date: ")
end = datetime.datetime.strptime(end_date, "%d/%m/%Y").timestamp()

r = r = requests.get(
    f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=eur&from={start}&to={end}").text

r = json.loads(r)

#The old logic for investment days must be removed and the logic of falling days differentiated into its own function
#The time zone also needs to be corrected
prices = Cleaned_list('prices', r)
price_d =prices.get_header()
invest_days = Analyze('prices', price_d)
invest_days.get_investment_days()
maxs = invest_days.get_max_prof()
volumes = Cleaned_list('total_volumes', r)
volumes_d = volumes.get_header()
max_volumes = Analyze('total_volumes', volumes_d)
max_volumes.get_max_volume()

