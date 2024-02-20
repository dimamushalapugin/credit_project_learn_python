import datetime
import pandas as pd
from webapp.risk.logger import logging
from holidays_ru import check_holiday


# class PeriodDataProcessor:
#     def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
#         self.data = data
#         self.period_month = self.extract_file(data)[2]
#         self.start_date = date_of_issue
#         self.last_day_of_month = pd.to_datetime(self.start_date) + pd.offsets.MonthEnd(0)
#         try:
#             self.percent = float(interest_rate)
#         except ValueError:
#             logging.info("Interest rate is None")
#             self.percent = 0.0
#         self.bank_day_percent = bank_day_percent
#         self.output_data = None
#         self.output_data_new = None  # Add this line to initialize the attribute
#
#     pd.set_option('display.max_columns', 25)
#     pd.set_option('display.max_rows', 500)
#
#     @staticmethod
#     def extract_file(data_json):
#         df = pd.DataFrame(data_json)
#         start_date = pd.to_datetime(df['Дата погашения Основного долга'], origin='1899-12-30', unit='D')
#         df['Дата погашения Основного долга'] = start_date
#
#         # Convert the "Дата погашения" column to datetime format
#         df['Дата погашения Основного долга'] = pd.to_datetime(df['Дата погашения Основного долга'])
#         # считает кол-во строк в первом столбце
#         num_rows = df.shape[0]
#
#         # Extract the month and year from the first cell of the "Дата погашения" column
#         month_year = df['Дата погашения Основного долга'][0].strftime('%B %Y')
#         return month_year, df, num_rows
#
#     def create_dataframe(self):
#         self.output_data = pd.DataFrame({
#             '№': range(0, self.period_month),
#             'Дата начала периода': pd.date_range(start=self.start_date, periods=self.period_month, freq='MS'),
#             'Дата окончания периода': pd.date_range(start=self.start_date, periods=self.period_month,
#                                                     freq='MS') + pd.offsets.MonthEnd(),
#             'Дата уплаты процентов': pd.date_range(start=self.start_date, periods=self.period_month,
#                                                    freq='MS') + pd.offsets.MonthEnd(),
#             'Остаток ОД на начало периода': 0,
#             'Количество дней до погашения ОД': 0,
#             'Остаток ОД на конец периода': 0,
#             'Количество дней после погашения ОД': 0,
#             'Сумма процентов до погашения ОД': 0,
#             'Сумма процентов после погашения ОД': 0,
#             'Общая сумма процентов': 0})
#
#         new_row = pd.DataFrame(
#             {'№': [0], 'Дата начала периода': [self.start_date], 'Дата окончания периода': [self.last_day_of_month],
#              'Дата уплаты процентов': [self.last_day_of_month]})
#         self.output_data = pd.concat([new_row, self.output_data], ignore_index=True)
#         self.output_data['Дата начала периода'] = pd.to_datetime(self.output_data['Дата начала периода'])
#         self.output_data['Дата окончания периода'] = pd.to_datetime(self.output_data['Дата окончания периода'])
#         self.output_data = self.output_data.reset_index(drop=True)
#         self.output_data['№'] = self.output_data.index
#
#     @staticmethod
#     def is_weekend_or_holiday(day):
#         return day.weekday() >= 5 or check_holiday(day)
#
#     def get_next_working_day(self, day):
#         while self.is_weekend_or_holiday(day):
#             day += pd.DateOffset(days=1)
#         return day
#
#     def get_last_working_day(self, day):
#         while self.is_weekend_or_holiday(day):
#             day -= pd.DateOffset(days=1)
#         return day
#
#     def define_year(self, index):
#         date_value = self.output_data_new.loc[index, 'Дата окончания периода']
#         if pd.notnull(date_value):  # Check for non-null values
#             date_object = pd.to_datetime(date_value)
#             year = date_object.year
#         else:
#             year = 365
#             logging.info("Date value is null or invalid")  # Handle the case where the date value is null or invalid
#         days_in_current_year = datetime.date(year, 12, 31).timetuple().tm_yday
#         return days_in_current_year
#
#     def process_data(self, bank_day_percent):
#         self.output_data['Дата начала периода'] = pd.to_datetime(self.output_data['Дата начала периода'])
#         month_year_table = self.output_data['Дата начала периода'][0].strftime('%B %Y')
#
#         if month_year_table == self.extract_file(self.data)[0]:
#             new_row_xlsx = self.extract_file(self.data)[1]
#             self.output_data_new = pd.concat([self.output_data, new_row_xlsx], axis=1).drop(
#                 columns='№')  # Change to self.output_data_new
#         else:
#             new_row_xlsx = pd.DataFrame(
#                 {'№': [0], 'Дата погашения Основного долга': 0, 'Сумма погашения Основного долга': 0})
#             extract_file_new = pd.concat([new_row_xlsx, self.extract_file(self.data)[1]], ignore_index=True).drop(
#                 columns='№')
#             self.output_data_new = pd.concat([self.output_data, extract_file_new],
#                                              axis=1)  # Change to self.output_data_new
#
#         if self.output_data_new.loc[0, 'Дата погашения Основного долга'] == 0:  # Change to self.output_data_new
#             """"делаем расчет для нулевой строки"""
#             zero_line = (self.output_data_new.loc[0, 'Дата окончания периода'] - self.output_data_new.loc[
#                 0, 'Дата начала периода']).days
#             self.output_data_new.loc[0, 'Общая сумма процентов'] = round(
#                 (self.output_data_new['Сумма погашения Основного долга'].sum() * self.percent
#                  / self.define_year(index=0) * zero_line), 2)
#             self.output_data_new.loc[0, 'Количество дней до погашения ОД'] = zero_line
#             self.output_data_new.loc[0, 'Остаток ОД на начало периода'] = round(self.output_data_new[
#                                                                                     'Сумма погашения Основного долга'].sum(),
#                                                                                 2)
#             self.output_data_new.loc[0, 'Количество дней после погашения ОД'] = 0
#             self.output_data_new.loc[0, 'Остаток ОД на конец периода'] = round(self.output_data_new[
#                                                                                    'Сумма погашения Основного долга'].sum(),
#                                                                                2)
#             self.output_data_new.loc[0, 'Сумма процентов до погашения ОД'] = round(
#                 (self.output_data_new['Сумма погашения Основного долга'].sum() * self.percent
#                  / self.define_year(index=0) * zero_line), 2)
#             massive = 1
#         else:
#             massive = 0
#
#         """"делаем расчет для всех остальных строк"""
#         for i in range(massive, len(self.output_data_new)):
#             first_line_0_i = (
#                     self.output_data_new.loc[i, 'Дата погашения Основного долга'] - self.output_data_new.loc[
#                 i, 'Дата начала периода']).days
#             first_line_1_i = (self.output_data_new.loc[i, 'Дата окончания периода'] - self.output_data_new.loc[
#                 i, 'Дата погашения Основного долга']).days
#             principal_debt_0_i = round(self.output_data_new['Сумма погашения Основного долга'].iloc[i:].sum(), 2)
#             principal_debt_1_i = round(self.output_data_new['Сумма погашения Основного долга'].iloc[(i + 1):].sum(),
#                                        2)
#             principal_monthpay_0_i = round(
#                 principal_debt_0_i * self.percent / self.define_year(index=i) * first_line_0_i, 2)
#             principal_monthpay_1_i = round(
#                 principal_debt_1_i * self.percent / self.define_year(index=i) * first_line_1_i, 2)
#
#             self.output_data_new.loc[i, 'Количество дней до погашения ОД'] = first_line_0_i
#             self.output_data_new.loc[i, 'Остаток ОД на начало периода'] = round(principal_debt_0_i, 2)
#             self.output_data_new.loc[i, 'Количество дней после погашения ОД'] = first_line_1_i
#             self.output_data_new.loc[i, 'Остаток ОД на конец периода'] = round(principal_debt_1_i, 2)
#             self.output_data_new.loc[i, 'Сумма процентов до погашения ОД'] = principal_monthpay_0_i
#             self.output_data_new.loc[i, 'Сумма процентов после погашения ОД'] = principal_monthpay_1_i
#             self.output_data_new.loc[i, 'Общая сумма процентов'] = round(
#                 principal_monthpay_0_i + principal_monthpay_1_i, 2)
#         self.output_data_new = self.output_data_new.fillna(0)
#
#         if bank_day_percent == 'ПАО «МОСКОВСКИЙ КРЕДИТНЫЙ БАНК»':
#             self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
#                                                              .apply(self.get_next_working_day))
#         elif bank_day_percent in ['АО «СМП БАНК»', 'АО «ИНВЕСТТОРГБАНК»']:
#             self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
#                                                              .apply(self.get_last_working_day))
#         elif bank_day_percent == 'ПАО «АК БАРС» БАНК':
#             self.output_data_new['Дата уплаты процентов'] += pd.DateOffset(days=10)
#             self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
#                                                              .apply(self.get_next_working_day))
#         elif bank_day_percent == 'АО КБ «УРАЛ ФД»':
#             self.output_data_new['Дата уплаты процентов'] += pd.DateOffset(days=1)
#             self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
#                                                              .apply(self.get_next_working_day))
#         else:
#             self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
#                                                              .apply(self.get_next_working_day))
#
#         self.output_data_new['Дата начала периода'] = self.output_data_new['Дата начала периода'].apply(
#             lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
#         self.output_data_new['Дата окончания периода'] = self.output_data_new['Дата окончания периода'].apply(
#             lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
#         self.output_data_new['Дата погашения Основного долга'] = self.output_data_new[
#             'Дата погашения Основного долга'].apply(lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
#         self.output_data_new['Дата уплаты процентов'] = self.output_data_new['Дата уплаты процентов'].apply(
#             lambda x: x.strftime('%Y-%m-%d') if x != 0 else 0)
#
#         # Save the updated output_data to an Excel file
#         self.output_data_new.to_excel('updated_output_data.xlsx', index=False)  # Change to self.output_data_new
#
#     # Inside the PeriodDataProcessor class
#     def print_output_data(self, bank_day_percent):
#         self.create_dataframe()
#         self.process_data(bank_day_percent)
#         return self.output_data_new


class Bank:
    def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
        self.data = data
        self.start_date = date_of_issue
        self.last_day_of_month = pd.to_datetime(self.start_date) + pd.offsets.MonthEnd(0)
        try:
            self.percent = float(interest_rate)
        except ValueError:
            logging.info("Interest rate is None")
            self.percent = 0.0
        self.bank_day_percent = bank_day_percent
        self.output_data = None
        self.output_data_new = None  # Add this line to initialize the attribute
        self.period_month = self.extract_file(data)[2]

    pd.set_option('display.max_columns', 25)
    pd.set_option('display.max_rows', 500)

    @staticmethod
    def extract_file(data_json):
        print(data_json)
        df = pd.DataFrame(data_json)
        start_date = pd.to_datetime(df['Дата погашения Основного долга'], origin='1899-12-30', unit='D')
        df['Дата погашения Основного долга'] = start_date

        # Convert the "Дата погашения" column to datetime format
        df['Дата погашения Основного долга'] = pd.to_datetime(df['Дата погашения Основного долга'])
        # считает кол-во строк в первом столбце
        num_rows = df.shape[0]

        # Extract the month and year from the first cell of the "Дата погашения" column
        month_year = df['Дата погашения Основного долга'][0].strftime('%B %Y')
        print(df)
        return month_year, df, num_rows

    @staticmethod
    def is_weekend_or_holiday(day):
        return day.weekday() >= 5 or check_holiday(day)

    def get_next_working_day(self, day):
        while self.is_weekend_or_holiday(day):
            day += pd.DateOffset(days=1)
        return day

    def get_last_working_day(self, day):
        while self.is_weekend_or_holiday(day):
            day -= pd.DateOffset(days=1)
        return day

    def define_year(self, index):
        date_value = self.output_data_new.loc[index, 'Дата окончания периода']
        if pd.notnull(date_value):  # Check for non-null values
            date_object = pd.to_datetime(date_value)
            year = date_object.year
        else:
            year = 365
            logging.info("Date value is null or invalid")  # Handle the case where the date value is null or invalid
        days_in_current_year = datetime.date(year, 12, 31).timetuple().tm_yday
        print(days_in_current_year)
        return days_in_current_year

    def calculate_interest(self):
        raise NotImplementedError("Subclasses must implement this method.")


# Дочерние классы, представляющие разные банки
class AkBarsBank(Bank):
    def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
        super().__init__(data, interest_rate, date_of_issue, bank_day_percent)
        print('Bank')
        print(data)

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
            'Общая сумма процентов': 0})

        new_row = pd.DataFrame(
            {'№': [0], 'Дата начала периода': [self.start_date], 'Дата окончания периода': [self.last_day_of_month],
             'Дата уплаты процентов': [self.last_day_of_month]})
        self.output_data = pd.concat([new_row, self.output_data], ignore_index=True)
        self.output_data['Дата начала периода'] = pd.to_datetime(self.output_data['Дата начала периода'])
        self.output_data['Дата окончания периода'] = pd.to_datetime(self.output_data['Дата окончания периода'])
        self.output_data = self.output_data.reset_index(drop=True)
        self.output_data['№'] = self.output_data.index

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

        if self.bank_day_percent == 'ПАО «МОСКОВСКИЙ КРЕДИТНЫЙ БАНК»':
            self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
                                                             .apply(self.get_next_working_day))
        elif self.bank_day_percent in ['АО «СМП БАНК»', 'АО «ИНВЕСТТОРГБАНК»']:
            self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
                                                             .apply(self.get_last_working_day))
        elif self.bank_day_percent == 'ПАО «АК БАРС» БАНК':
            self.output_data_new['Дата уплаты процентов'] += pd.DateOffset(days=10)
            self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
                                                             .apply(self.get_next_working_day))
        elif self.bank_day_percent == 'АО КБ «УРАЛ ФД»':
            self.output_data_new['Дата уплаты процентов'] += pd.DateOffset(days=1)
            self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
                                                             .apply(self.get_next_working_day))
        else:
            self.output_data_new['Дата уплаты процентов'] = (self.output_data_new['Дата уплаты процентов']
                                                             .apply(self.get_next_working_day))

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

    def print_output_data(self):
        self.create_dataframe()
        self.process_data()
        return self.output_data_new

    def calculate_interest(self):
        # Расчет процентов для банка Ак Барс
        return

# class SberBank(Bank):
#     def __init__(self, loan_amount, interest_rate):
#         super().__init__("Сбербанк", loan_amount, interest_rate)
#         self.interest_payment_date = 15  # Погашение процентов каждый 15-й день месяца
#
#     def calculate_interest(self):
#         # Расчет процентов для Сбербанка
#         return
#
#
# class MetallinvestBank(Bank):
#     def __init__(self, loan_amount, interest_rate):
#         super().__init__("Металлинвест", loan_amount, interest_rate)
#         self.interest_payment_date = 20  # Погашение процентов каждый 20-й день месяца
#
#     def calculate_interest(self):
#         # Расчет процентов для Металлинвеста
#         return


# Пример использования
# ak_bars = AkBarsBank(10000, 5)
# print("Total Interest for Ак Барс:", ak_bars.calculate_interest())
