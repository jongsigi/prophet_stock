import pandas as pd
from datetime import datetime

def sys01_filter(years, past_offset, save_raw_path):
    today = datetime.today().strftime("%Y%m%d")

    for year in years:
        processed_total_data_file_name = f"{year}_total_{str(past_offset)}_{today}.xlsx"
        processed_total_data_file_path = save_raw_path + '/' + processed_total_data_file_name
        p_t_data = pd.read_excel(processed_total_data_file_path, engine='openpyxl')
        
        # filtered_stock_code_2023/2024에 대해 위에서 초기화를 해주니 오히려 데이터를 못가지고 있음 (왜그런지는 전역/지역변수 공부해볼것)
        # filtered_stock_code_2023/2024 변수 생성 후, sys01 조건인 All Trend_del > 0 & t0>0 조건
        globals()['filtered_stock_code_{}'.format(str(year))] = p_t_data.loc[(p_t_data['bool'] == True) & (p_t_data['t0']>0) ,['code', 'name']]

    reset_index_2023 = filtered_stock_code_2023.reset_index(drop=True, inplace=False)
    reset_index_2024 = filtered_stock_code_2024.reset_index(drop=True, inplace=False)
    
    filtered_target = pd.DataFrame(columns=['code', 'name'])
    target_num = 0

    for row in range(len(reset_index_2024)):
        if (reset_index_2023['code'] == reset_index_2024['code'][row]).any():
            filtered_target.loc[target_num] = reset_index_2024.loc[row]
            target_num += 1
        else:
            pass
    filtered_target_file_name = "filtered_target.xlsx"
    filtered_target_file_path = save_raw_path + '/' + filtered_target_file_name
    filtered_target.to_excel(filtered_target_file_path, index=False)

