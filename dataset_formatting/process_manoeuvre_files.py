import os
import pandas as pd

RAW_DATA_DIR = "../raw_data/"
MAX_NUM_COLS = 100
BURN_COL_SPAN = 15
BURNS_COL_START = 11
SPOT_COL_MODIFIER = 1

for file_name in os.listdir(RAW_DATA_DIR):
    print(file_name)

    if not file_name.startswith("ja"):
        continue

    burns_col_start = BURNS_COL_START
    if file_name.endswith("readme"):
        continue
    elif file_name.startswith("sp"):
        burns_col_start += SPOT_COL_MODIFIER

    df_manoeuvre_history = pd.read_csv(RAW_DATA_DIR + file_name, delim_whitespace=True, names=range(MAX_NUM_COLS))



    for row_index in range(df_manoeuvre_history.shape[0]):
        print()
        print(df_manoeuvre_history.iloc[row_index][burns_col_start-3])
        num_burns = int(round(df_manoeuvre_history.iloc[row_index][burns_col_start - 1]))
        print("num_burns", num_burns)
        for burn_num in range(num_burns):
            burn_year = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN]
            burn_day = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 1]
            burn_hour = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 2]
            burn_minute = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 3]
            burn_seconds = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 4]
            radial_acc = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 9]
            in_track_acc = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 10]
            cross_track_acc = df_manoeuvre_history.iloc[row_index][burns_col_start + burn_num * BURN_COL_SPAN + 11]
            print(burn_year)
            print(radial_acc)
            print(in_track_acc)
            print(cross_track_acc)

    #quit()






    #print(df_manoeuvre_history[10].mean())

