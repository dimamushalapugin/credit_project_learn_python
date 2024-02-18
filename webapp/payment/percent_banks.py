import datetime
import pandas as pd
from webapp.risk.logger import logging


class PeriodDataProcessor:
    def __init__(self, data, interest_rate, date_of_issue):
        self.data = data
        self.period_month = self.extract_file(data)[2]
        self.start_date = date_of_issue
        self.last_day_of_month = pd.to_datetime(self.start_date) + pd.offsets.MonthEnd(0)
        self.percent = float(interest_rate)
        self.output_data = None
        self.output_data_new = None  # Add this line to initialize the attribute

    pd.set_option('display.max_columns', 25)
    pd.set_option('display.max_rows', 500)

    @staticmethod
    def extract_file(data_json):
        df = pd.DataFrame(data_json)
        start_date = pd.to_datetime(df['Дата погашения Основного долга'], origin='1899-12-30', unit='D')
        df['Дата погашения Основного долга'] = start_date

        # Convert the "Дата погашения" column to datetime format
        df['Дата погашения Основного долга'] = pd.to_datetime(df['Дата погашения Основного долга'])
        # считает кол-во строк в первом столбце
        num_rows = df.shape[0]

        # Extract the month and year from the first cell of the "Дата погашения" column
        month_year = df['Дата погашения Основного долга'][0].strftime('%B %Y')
        return month_year, df, num_rows

    def create_dataframe(self):
        self.output_data = pd.DataFrame({
            '№': range(0, self.period_month),
            'Дата начала периода': pd.date_range(start=self.start_date, periods=self.period_month, freq='MS'),
            'Дата окончания периода': pd.date_range(start=self.start_date, periods=self.period_month,
                                                    freq='MS') + pd.offsets.MonthEnd(),
            'Дата уплаты процентов': pd.date_range(start=self.start_date, periods=self.period_month,
                                                   freq='MS') + pd.offsets.MonthEnd(),
            'Остаток ОД на начало периода': 0,
            'Количество дней до погашения ОД': 0,
            'Остаток ОД на конец периода': 0,
            'Количество дней после погашения ОД': 0,
            'Сумма процентов до погашения ОД': 0,
            'Сумма процентов после погашения ОД': 0,
            'Общая сумма процентов': 0
        })

        new_row = pd.DataFrame(
            {'№': [0], 'Дата начала периода': [self.start_date], 'Дата окончания периода': [self.last_day_of_month],
             'Дата уплаты процентов': [self.last_day_of_month]})
        self.output_data = pd.concat([new_row, self.output_data], ignore_index=True)
        self.output_data['Дата начала периода'] = pd.to_datetime(self.output_data['Дата начала периода'])
        self.output_data['Дата окончания периода'] = pd.to_datetime(self.output_data['Дата окончания периода'])
        self.output_data = self.output_data.reset_index(drop=True)
        self.output_data['№'] = self.output_data.index

    def define_year(self, index):
        date_value = self.output_data_new.loc[index, 'Дата окончания периода']
        if pd.notnull(date_value):  # Check for non-null values
            date_object = pd.to_datetime(date_value)
            year = date_object.year
        else:
            year = 365
            logging.info("Date value is null or invalid")  # Handle the case where the date value is null or invalid
        days_in_current_year = datetime.date(year, 12, 31).timetuple().tm_yday
        return days_in_current_year

    def process_data(self):
        self.output_data['Дата начала периода'] = pd.to_datetime(self.output_data['Дата начала периода'])
        month_year_table = self.output_data['Дата начала периода'][0].strftime('%B %Y')

        if month_year_table == self.extract_file(self.data)[0]:
            new_row_xlsx = self.extract_file(self.data)[1]
            self.output_data_new = pd.concat([self.output_data, new_row_xlsx], axis=1).drop(
                columns='№')  # Change to self.output_data_new
        else:
            new_row_xlsx = pd.DataFrame(
                {'№': [0], 'Дата погашения Основного долга': 0, 'Сумма погашения Основного долга': 0})
            extract_file_new = pd.concat([new_row_xlsx, self.extract_file(self.data)[1]], ignore_index=True).drop(
                columns='№')
            self.output_data_new = pd.concat([self.output_data, extract_file_new],
                                             axis=1)  # Change to self.output_data_new

        if self.output_data_new.loc[0, 'Дата погашения Основного долга'] == 0:  # Change to self.output_data_new
            """"делаем расчет для нулевой строки"""
            zero_line = (self.output_data_new.loc[0, 'Дата окончания периода'] - self.output_data_new.loc[
                0, 'Дата начала периода']).days
            self.output_data_new.loc[0, 'Общая сумма процентов'] = round(
                (self.output_data_new['Сумма погашения Основного долга'].sum() * self.percent
                 / self.define_year(index=0) * zero_line), 2)
            self.output_data_new.loc[0, 'Количество дней до погашения ОД'] = zero_line
            self.output_data_new.loc[0, 'Остаток ОД на начало периода'] = round(self.output_data_new[
                                                                                    'Сумма погашения Основного долга'].sum(),
                                                                                2)
            self.output_data_new.loc[0, 'Количество дней после погашения ОД'] = 0
            self.output_data_new.loc[0, 'Остаток ОД на конец периода'] = round(self.output_data_new[
                                                                                   'Сумма погашения Основного долга'].sum(),
                                                                               2)
            self.output_data_new.loc[0, 'Сумма процентов до погашения ОД'] = round(
                (self.output_data_new['Сумма погашения Основного долга'].sum() * self.percent
                 / self.define_year(index=0) * zero_line), 2)
            massive = 1
        else:
            massive = 0

        """"делаем расчет для всех остальных строк"""
        for i in range(massive, len(self.output_data_new)):
            first_line_0_i = (
                    self.output_data_new.loc[i, 'Дата погашения Основного долга'] - self.output_data_new.loc[
                i, 'Дата начала периода']).days
            first_line_1_i = (self.output_data_new.loc[i, 'Дата окончания периода'] - self.output_data_new.loc[
                i, 'Дата погашения Основного долга']).days
            principal_debt_0_i = round(self.output_data_new['Сумма погашения Основного долга'].iloc[i:].sum(), 2)
            principal_debt_1_i = round(self.output_data_new['Сумма погашения Основного долга'].iloc[(i + 1):].sum(),
                                       2)
            principal_monthpay_0_i = round(
                principal_debt_0_i * self.percent / self.define_year(index=i) * first_line_0_i, 2)
            principal_monthpay_1_i = round(
                principal_debt_1_i * self.percent / self.define_year(index=i) * first_line_1_i, 2)

            self.output_data_new.loc[i, 'Количество дней до погашения ОД'] = first_line_0_i
            self.output_data_new.loc[i, 'Остаток ОД на начало периода'] = round(principal_debt_0_i, 2)
            self.output_data_new.loc[i, 'Количество дней после погашения ОД'] = first_line_1_i
            self.output_data_new.loc[i, 'Остаток ОД на конец периода'] = round(principal_debt_1_i, 2)
            self.output_data_new.loc[i, 'Сумма процентов до погашения ОД'] = principal_monthpay_0_i
            self.output_data_new.loc[i, 'Сумма процентов после погашения ОД'] = principal_monthpay_1_i
            self.output_data_new.loc[i, 'Общая сумма процентов'] = round(
                principal_monthpay_0_i + principal_monthpay_1_i, 2)
        self.output_data_new = self.output_data_new.fillna(0)
        self.output_data_new['Дата начала периода'] = self.output_data_new['Дата начала периода'].apply(
            lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
        self.output_data_new['Дата окончания периода'] = self.output_data_new['Дата окончания периода'].apply(
            lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
        self.output_data_new['Дата погашения Основного долга'] = self.output_data_new[
            'Дата погашения Основного долга'].apply(lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
        self.output_data_new['Дата уплаты процентов'] = self.output_data_new['Дата уплаты процентов'].apply(
            lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
        # Save the updated output_data to an Excel file
        self.output_data_new.to_excel('updated_output_data.xlsx', index=False)  # Change to self.output_data_new

    # Inside the PeriodDataProcessor class
    def print_output_data(self):
        self.create_dataframe()
        self.process_data()
        return self.output_data_new
