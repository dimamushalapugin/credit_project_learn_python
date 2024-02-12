import pandas as pd
from datetime import datetime
import datetime

pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 500)


def extract_file():
    # Замените 'file.xlsx' на путь к вашему файлу xlsx
    file_path = 'Образец расчета Learn Python.xlsx'

    # Прочитать файл xlsx
    data = pd.read_excel(file_path)

    # Вывести три столбца из таблицы
    output_data_xslx = data.iloc[:, :3]  # Выбираем все строки и первые три столбца

    # print(output_data_xslx)

    # Convert the "Дата погашения" column to datetime format
    data['Дата погашения Основного долга'] = pd.to_datetime(data['Дата погашения Основного долга'])
    # считает кол-во строк в первом столбце
    num_rows = data.shape[0]
    print(num_rows)

    # Extract the month and year from the first cell of the "Дата погашения" column
    month_year = data['Дата погашения Основного долга'][0].strftime('%B %Y')
    # print(month_year)
    return month_year, output_data_xslx, num_rows


#key parameters
percent = 0.10
start_date = '2020-10-15'
last_day_of_month = pd.to_datetime(start_date) + pd.offsets.MonthEnd(0)
period_month = extract_file()[2]


class PeriodDataProcessor:
    def __init__(self, period_month, start_date, last_day_of_month, percent):
        self.period_month = period_month
        self.start_date = start_date
        self.last_day_of_month = last_day_of_month
        self.percent = percent
        self.output_data = None
        self.output_data_new = None  # Add this line to initialize the attribute

    def create_dataframe(self):
        self.output_data = pd.DataFrame({
            '№': range(0, self.period_month),
            'Дата начала периода': pd.date_range(start=self.start_date, periods=self.period_month, freq='MS'),
            'Дата окончания периода': pd.date_range(start=self.start_date, periods=self.period_month, freq='MS') + pd.offsets.MonthEnd(),
            'Дата уплаты процентов': pd.date_range(start=self.start_date, periods=self.period_month, freq='MS') + pd.offsets.MonthEnd(),
            'Остаток ОД на начало периода': 0,
            'Количество дней до погашения ОД': 0,
            'Остаток ОД на конец периода': 0,
            'Количество дней после погашения ОД': 0,
            'Сумма процентов до погашения ОД': 0,
            'Сумма процентов после погашения ОД': 0,
            'Общая сумма процентов': 0
        })

        new_row = pd.DataFrame({'№': [0], 'Дата начала периода': [self.start_date], 'Дата окончания периода': [self.last_day_of_month],
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
            print(year)  # Replace with the appropriate handling of the year value
        else:
            year = 365
            print("Date value is null or invalid")  # Handle the case where the date value is null or invalid
        days_in_current_year = datetime.date(year, 12, 31).timetuple().tm_yday
        print(days_in_current_year)
        return days_in_current_year


    def process_data(self):
        self.output_data['Дата начала периода'] = pd.to_datetime(self.output_data['Дата начала периода'])
        month_year_table = self.output_data['Дата начала периода'][0].strftime('%B %Y')

        if month_year_table == extract_file()[0]:
            new_row_xlsx = extract_file()[1]
            self.output_data_new = pd.concat([self.output_data, new_row_xlsx], axis=1).drop(columns='№')  # Change to self.output_data_new
        else:
            new_row_xlsx = pd.DataFrame(
                {'№': [0], 'Дата погашения Основного долга': 0, 'Сумма погашения Основного долга': 0})
            extract_file_new = pd.concat([new_row_xlsx, extract_file()[1]], ignore_index=True).drop(columns='№')
            self.output_data_new = pd.concat([self.output_data, extract_file_new],
                                             axis=1)  # Change to self.output_data_new

        if self.output_data_new.loc[0, 'Дата погашения Основного долга'] == 0:  # Change to self.output_data_new
            print('zero')
            """"делаем расчет для нулевой строки"""
            zero_line = (self.output_data_new.loc[0, 'Дата окончания периода'] - self.output_data_new.loc[
                0, 'Дата начала периода']).days
            self.output_data_new.loc[0, 'Общая сумма процентов'] = round(
                (self.output_data_new['Сумма погашения Основного долга'].sum() * self.percent
                 / self.define_year(index=0) * zero_line), 2)
            self.output_data_new.loc[0, 'Количество дней до погашения ОД'] = zero_line
            self.output_data_new.loc[0, 'Остаток ОД на начало периода'] = self.output_data_new['Сумма погашения Основного долга'].sum()
            self.output_data_new.loc[0, 'Количество дней после погашения ОД'] = 0
            self.output_data_new.loc[0, 'Остаток ОД на конец периода'] = self.output_data_new['Сумма погашения Основного долга'].sum()
            self.output_data_new.loc[0, 'Сумма процентов до погашения ОД'] = round(
                (self.output_data_new['Сумма погашения Основного долга'].sum() * self.percent
                 / self.define_year(index=0) * zero_line), 2)
            massive = 1
        else:
            print('Not zero')
            massive = 0

        """"делаем расчет для всех остальных строк"""
        for i in range(massive, len(self.output_data_new)):
            first_line_0_i = (
                    self.output_data_new.loc[i, 'Дата погашения Основного долга'] - self.output_data_new.loc[
                i, 'Дата начала периода']).days
            first_line_1_i = (self.output_data_new.loc[i, 'Дата окончания периода'] - self.output_data_new.loc[
                i, 'Дата погашения Основного долга']).days
            principal_debt_0_i = round(self.output_data_new['Сумма погашения Основного долга'].iloc[i:].sum(), 2)
            principal_debt_1_i = round(self.output_data_new['Сумма погашения Основного долга'].iloc[(i + 1):].sum(), 2)
            principal_monthpay_0_i = round(principal_debt_0_i * self.percent / self.define_year(index=i) * first_line_0_i, 2)
            principal_monthpay_1_i = round(principal_debt_1_i * self.percent / self.define_year(index=i) * first_line_1_i, 2)

            self.output_data_new.loc[i, 'Количество дней до погашения ОД'] = first_line_0_i
            self.output_data_new.loc[i, 'Остаток ОД на начало периода'] = principal_debt_0_i
            self.output_data_new.loc[i, 'Количество дней после погашения ОД'] = first_line_1_i
            self.output_data_new.loc[i, 'Остаток ОД на конец периода'] = principal_debt_1_i
            self.output_data_new.loc[i, 'Сумма процентов до погашения ОД'] = principal_monthpay_0_i
            self.output_data_new.loc[i, 'Сумма процентов после погашения ОД'] = principal_monthpay_1_i
            self.output_data_new.loc[i, 'Общая сумма процентов'] = round(principal_monthpay_0_i + principal_monthpay_1_i, 2)

        # Save the updated output_data to an Excel file
        self.output_data_new.to_excel('updated_output_data.xlsx', index=False)  # Change to self.output_data_new

    # Inside the PeriodDataProcessor class
    def print_output_data(self):
        print(self.output_data_new)

# Example usage
processor = PeriodDataProcessor(period_month, start_date, last_day_of_month, percent)
processor.create_dataframe()
processor.process_data()
processor.print_output_data()
processor.define_year(index=0)

