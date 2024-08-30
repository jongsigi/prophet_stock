import os
from sys01.sys01_process import sys01_process
from sys01.sys01_base import *
from sys01.sys01_filter import *
from sys01.sys01_order import *

class Main:
    def __init__(self, file_name, years, fcast_time, past_offset, capital):
        self.file_name = file_name + '.xlsx'
        self.years = years
        self.fcast_time = fcast_time
        self.past_offset = past_offset
        self.capital = capital
        
        this_week = get_week_number()
        save_raw_path = os.getcwd() + "/raw/sys01/ww" + str(this_week)
        makedirs(save_raw_path)

        sys01_process(self.file_name, 
                      self.years, 
                      fcast_time=self.fcast_time,
                      past_offset=self.past_offset)
        sys01_process.my_apply_prophet(self, save_raw_path=save_raw_path)

        sys01_filter(self.years, self.past_offset, save_raw_path)
        
        order_year = '2024'
        sys01_order(order_year, self.fcast_time, self.past_offset, save_filtered_path=save_raw_path, capital=self.capital)

if __name__ == "__main__":
    Main("target", ['2024', '2023'], 10, 5, 5000000)