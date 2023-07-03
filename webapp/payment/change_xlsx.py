import pandas as pd
from holidays_ru import check_holiday


def change_of_date(request_filename):
    df = pd.read_excel(request_filename)

    def is_weekend_or_holiday(day):
        return day.weekday() >= 5 or check_holiday(day)

    def get_next_working_day(day):
        while is_weekend_or_holiday(day):
            day += pd.DateOffset(days=1)
        return day

    df['payment_date'] = df['payment_date'].apply(get_next_working_day)
    return df

