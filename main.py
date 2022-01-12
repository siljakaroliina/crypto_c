import datetime
import requests
import json
import pandas as pd
import numpy as np

class Cleaned_list:


    def __init__(self, header: str, data: dict):
        self.header = header
        self.data = data

    def get_data_for_header(self):
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

        return self.data
        


class Analyze(Cleaned_list):

    def __init__(self, header: str, data: dict):
        super().__init__(header, data)
        self.min_max = ()
        self.max_volume = ()
        self.decreased_days = 0

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
            
            if count > max_count:
                    max_count = count
                    count = 0
            h = i
        self.decreased_days = max_count
        return self.decreased_days

    def get_max_volume(self):
        data = self.data
        max_volume = 0

        for k, v in data.items():
            if k > max_volume:
                max_volume = k
                day_of_max = data[max_volume]
   
        day_of_max = day_of_max.strftime('%d-%m-%y')
        self.max_volume = day_of_max, max_volume
        return self.max_volume
    
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

            self.min_max = self.data[key_of_max].strftime('%d-%m-%y'), key_of_max, self.data[key_of_min].strftime('%d-%m-%y'), key_of_min, max_prof
            return self.min_max

    def print_days(self):

      
        if len(self.min_max) == 0:
            pass
        else:
            day_to_buy = self.min_max[2]
            day_to_sell = self.min_max[0]
            purchase_price = self.min_max[3]
            selling_price = self.min_max[1]
            profit = self.min_max[4]

            if purchase_price == selling_price:
                print("It is not worth selling or buying during this period")
            else:
                print(f"Buy bitcoins on {day_to_buy}. The value of Bitcoin that day was: {purchase_price}.")
                print(f"{day_to_sell} is a good day to sell the bitcoins you bought, then their value is {selling_price}")
                print(f"For one bitcoin, the profit would be {profit}")
        
    def print_max_volume(self):

        if len(self.max_volume) == 0:
            pass
        else:
            max_volume = self.max_volume[1]
            max_volume_day = self.max_volume[0]
            print(f"The day when the trading volume was the highest is: {max_volume_day}, when the volume was:{max_volume:.2f} eur")
    
    def print_decreasing_days(self):

        if self.decreased_days == 0:
            pass
        else:
            print(f"Maximum amount of days bitcoin's price was decreasing: {self.decreased_days}")
        




start_date = '06/01/2022'
end_date = '12/01/2022'
#start_date = input("Eneter the start date: ")
start = datetime.datetime.strptime(start_date, "%d/%m/%Y").timestamp()

#end_date = input("Enter the end date: ")
end = datetime.datetime.strptime(end_date, "%d/%m/%Y").timestamp()

r = r = requests.get(
    f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=eur&from={start}&to={end}").text

r = json.loads(r)

#The time zone also needs to be corrected
prices = Cleaned_list('prices', r)
price_d =prices.get_data_for_header()
invest_days = Analyze('prices', price_d)
invest_days.get_investment_days()
maxs = invest_days.get_max_prof()
volumes = Cleaned_list('total_volumes', r)
volumes_d = volumes.get_data_for_header()
max_volumes = Analyze('total_volumes', volumes_d)
max_volumes.get_max_volume()
invest_days.print_days()
invest_days.print_decreasing_days()

