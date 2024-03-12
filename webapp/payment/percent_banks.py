import datetime
import pandas as pd
from holidays_ru import check_holiday
from webapp.risk.logger import logging
from webapp.payment.sql_queries import get_nearest_interest_rate


class Bank:
    def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
        self.data = data
        self.start_date = date_of_issue
        self.last_day_of_month = pd.to_datetime(self.start_date) + pd.offsets.MonthEnd(
            0
        )
        try:
            self.percent = float(interest_rate)
        except ValueError:
            logging.info("Interest rate is None")
            self.percent = 0.0
        self.bank_day_percent = bank_day_percent
        self.output_data = None
        self.output_data_new = None  # Add this line to initialize the attribute
        self.period_month = self.extract_file(data, self.start_date)[2]

    pd.set_option("display.max_columns", 25)
    pd.set_option("display.max_rows", 500)

    @staticmethod
    def extract_file(data_json, date_of_issue):
        df = pd.DataFrame(data_json)
        data_pogashenie = "Дата погашения Основного долга"
        start_date = pd.to_datetime(df[data_pogashenie], origin="1899-12-30", unit="D")
        df[data_pogashenie] = start_date

        # Convert the "Дата погашения" column to datetime format
        df[data_pogashenie] = pd.to_datetime(df[data_pogashenie])
        # считает кол-во строк в первом столбце
        num_rows = df.shape[0]

        # Extract the month and year from the first cell of the "Дата погашения" column
        month_year = df[data_pogashenie][0].strftime("%B %Y")
        last_day_payment = df[data_pogashenie].iloc[-1]
        start_limit = pd.to_datetime(date_of_issue)
        days_difference = (last_day_payment - start_limit).days
        return month_year, df, num_rows, days_difference

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
        date_value = self.output_data_new.loc[index, "Дата окончания периода"]
        if pd.notnull(date_value):  # Check for non-null values
            date_object = pd.to_datetime(date_value)
            year = date_object.year
        else:
            year = 365
            logging.info(
                "Date value is null or invalid"
            )  # Handle the case where the date value is null or invalid
        days_in_current_year = datetime.date(year, 12, 31).timetuple().tm_yday
        return days_in_current_year

    @staticmethod
    def define_year_test(data):
        if pd.notnull(data):  # Check for non-null values
            date_object = pd.to_datetime(data)
            year = date_object.year
        else:
            year = 365
            logging.info(
                "Date value is null or invalid"
            )  # Handle the case where the date value is null or invalid
        days_in_current_year = datetime.date(year, 12, 31).timetuple().tm_yday
        return days_in_current_year


# Дочерние классы, представляющие разные банки
class AkBarsBank(Bank):
    def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
        super().__init__(data, interest_rate, date_of_issue, bank_day_percent)

    def create_dataframe(self):
        self.output_data = pd.DataFrame(
            {
                "№": range(0, self.period_month),
                "Дата начала периода": pd.date_range(
                    start=self.start_date, periods=self.period_month, freq="MS"
                ),
                "Дата окончания периода": pd.date_range(
                    start=self.start_date, periods=self.period_month, freq="MS"
                )
                + pd.offsets.MonthEnd(),
                "Дата уплаты процентов": pd.date_range(
                    start=self.start_date, periods=self.period_month, freq="MS"
                )
                + pd.offsets.MonthEnd(),
                "Остаток ОД на начало периода": 0,
                "Количество дней до погашения ОД": 0,
                "Остаток ОД на конец периода": 0,
                "Количество дней после погашения ОД": 0,
                "Сумма процентов до погашения ОД": 0,
                "Сумма процентов после погашения ОД": 0,
                "Общая сумма процентов": 0,
            }
        )

        new_row = pd.DataFrame(
            {
                "№": [0],
                "Дата начала периода": [self.start_date],
                "Дата окончания периода": [self.last_day_of_month],
                "Дата уплаты процентов": [self.last_day_of_month],
            }
        )
        self.output_data = pd.concat([new_row, self.output_data], ignore_index=True)
        self.output_data["Дата начала периода"] = pd.to_datetime(
            self.output_data["Дата начала периода"]
        )
        self.output_data["Дата окончания периода"] = pd.to_datetime(
            self.output_data["Дата окончания периода"]
        )
        self.output_data = self.output_data.reset_index(drop=True)
        self.output_data["№"] = self.output_data.index

    def calculate_interest(self):
        self.output_data["Дата начала периода"] = pd.to_datetime(
            self.output_data["Дата начала периода"]
        )
        month_year_table = self.output_data["Дата начала периода"][0].strftime("%B %Y")

        if month_year_table == self.extract_file(self.data, self.start_date)[0]:
            new_row_xlsx = self.extract_file(self.data, self.start_date)[1]
            self.output_data_new = pd.concat(
                [self.output_data, new_row_xlsx], axis=1
            ).drop(
                columns="№"
            )  # Change to self.output_data_new
        else:
            new_row_xlsx = pd.DataFrame(
                {
                    "№": [0],
                    "Дата погашения Основного долга": 0,
                    "Сумма погашения Основного долга": 0,
                }
            )
            extract_file_new = pd.concat(
                [new_row_xlsx, self.extract_file(self.data, self.start_date)[1]],
                ignore_index=True,
            ).drop(columns="№")
            self.output_data_new = pd.concat(
                [self.output_data, extract_file_new], axis=1
            )  # Change to self.output_data_new

        if (
            self.output_data_new.loc[0, "Дата погашения Основного долга"] == 0
        ):  # Change to self.output_data_new
            """ "делаем расчет для нулевой строки"""
            zero_line = (
                self.output_data_new.loc[0, "Дата окончания периода"]
                - self.output_data_new.loc[0, "Дата начала периода"]
            ).days
            self.output_data_new.loc[0, "Общая сумма процентов"] = round(
                (
                    self.output_data_new["Сумма погашения Основного долга"].sum()
                    * self.percent
                    / self.define_year(index=0)
                    * zero_line
                ),
                2,
            )
            self.output_data_new.loc[0, "Количество дней до погашения ОД"] = zero_line
            self.output_data_new.loc[0, "Остаток ОД на начало периода"] = round(
                self.output_data_new["Сумма погашения Основного долга"].sum(), 2
            )
            self.output_data_new.loc[0, "Количество дней после погашения ОД"] = 0
            self.output_data_new.loc[0, "Остаток ОД на конец периода"] = round(
                self.output_data_new["Сумма погашения Основного долга"].sum(), 2
            )
            self.output_data_new.loc[0, "Сумма процентов до погашения ОД"] = round(
                (
                    self.output_data_new["Сумма погашения Основного долга"].sum()
                    * self.percent
                    / self.define_year(index=0)
                    * zero_line
                ),
                2,
            )
            massive = 1
        else:
            massive = 0

        """"делаем расчет для всех остальных строк"""
        for i in range(massive, len(self.output_data_new)):
            first_line_0_i = (
                self.output_data_new.loc[i, "Дата погашения Основного долга"]
                - self.output_data_new.loc[i, "Дата начала периода"]
            ).days
            first_line_1_i = (
                self.output_data_new.loc[i, "Дата окончания периода"]
                - self.output_data_new.loc[i, "Дата погашения Основного долга"]
            ).days
            principal_debt_0_i = round(
                self.output_data_new["Сумма погашения Основного долга"].iloc[i:].sum(),
                2,
            )
            principal_debt_1_i = round(
                self.output_data_new["Сумма погашения Основного долга"]
                .iloc[(i + 1) :]
                .sum(),
                2,
            )
            principal_monthpay_0_i = round(
                principal_debt_0_i
                * self.percent
                / self.define_year(index=i)
                * first_line_0_i,
                2,
            )
            principal_monthpay_1_i = round(
                principal_debt_1_i
                * self.percent
                / self.define_year(index=i)
                * first_line_1_i,
                2,
            )

            self.output_data_new.loc[i, "Количество дней до погашения ОД"] = (
                first_line_0_i
            )
            self.output_data_new.loc[i, "Остаток ОД на начало периода"] = round(
                principal_debt_0_i, 2
            )
            self.output_data_new.loc[i, "Количество дней после погашения ОД"] = (
                first_line_1_i
            )
            self.output_data_new.loc[i, "Остаток ОД на конец периода"] = round(
                principal_debt_1_i, 2
            )
            self.output_data_new.loc[i, "Сумма процентов до погашения ОД"] = (
                principal_monthpay_0_i
            )
            self.output_data_new.loc[i, "Сумма процентов после погашения ОД"] = (
                principal_monthpay_1_i
            )
            self.output_data_new.loc[i, "Общая сумма процентов"] = round(
                principal_monthpay_0_i + principal_monthpay_1_i, 2
            )
        self.output_data_new = self.output_data_new.fillna(0)

        if self.bank_day_percent == "ПАО «МОСКОВСКИЙ КРЕДИТНЫЙ БАНК»":
            self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
                "Дата уплаты процентов"
            ].apply(self.get_next_working_day)
        elif self.bank_day_percent in ["АО «СМП БАНК»", "АО «ИНВЕСТТОРГБАНК»"]:
            self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
                "Дата уплаты процентов"
            ].apply(self.get_last_working_day)
        elif self.bank_day_percent == "ПАО «АК БАРС» БАНК":
            self.output_data_new["Дата уплаты процентов"] += pd.DateOffset(days=10)
            self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
                "Дата уплаты процентов"
            ].apply(self.get_next_working_day)
        elif self.bank_day_percent == "АО КБ «УРАЛ ФД»":
            self.output_data_new["Дата уплаты процентов"] += pd.DateOffset(days=1)
            self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
                "Дата уплаты процентов"
            ].apply(self.get_next_working_day)
        else:
            self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
                "Дата уплаты процентов"
            ].apply(self.get_next_working_day)

        self.output_data_new["Дата начала периода"] = self.output_data_new[
            "Дата начала периода"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        self.output_data_new["Дата окончания периода"] = self.output_data_new[
            "Дата окончания периода"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        self.output_data_new["Дата погашения Основного долга"] = self.output_data_new[
            "Дата погашения Основного долга"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
            "Дата уплаты процентов"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)

        # Save the updated output_data to an Excel file
        self.output_data_new.to_excel(
            "updated_output_data.xlsx", index=False
        )  # Change to self.output_data_new

    def start_function(self):
        self.create_dataframe()
        self.calculate_interest()
        return self.output_data_new


class AlfaBank(Bank):
    def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
        super().__init__(data, interest_rate, date_of_issue, bank_day_percent)

    def create_dataframe(self):
        self.output_data = pd.DataFrame(
            {
                "№": range(0, self.period_month),
                "Дата начала периода": pd.date_range(
                    start=self.start_date, periods=self.period_month, freq="MS"
                ),
                "Дата окончания периода": pd.date_range(
                    start=self.start_date, periods=self.period_month, freq="MS"
                )
                + pd.offsets.MonthEnd(),
                "Дата уплаты процентов": pd.date_range(
                    start=self.start_date, periods=self.period_month, freq="MS"
                ),
                "Остаток ОД на начало периода": 0,
                "Количество дней до погашения ОД": 0,
                "Остаток ОД на конец периода": 0,
                "Количество дней после погашения ОД": 0,
                "Сумма процентов до погашения ОД": 0,
                "Сумма процентов после погашения ОД": 0,
                "Общая сумма процентов": 0,
            }
        )

        self.output_data["Дата уплаты процентов"] += pd.DateOffset(days=24)
        start_date = pd.to_datetime(self.start_date, format="%Y-%m-%d")
        start_month = start_date.replace(day=25)
        new_row = pd.DataFrame(
            {
                "№": [0],
                "Дата начала периода": [self.start_date],
                "Дата окончания периода": [self.last_day_of_month],
                "Дата уплаты процентов": [start_month],
            }
        )
        self.output_data = pd.concat([new_row, self.output_data], ignore_index=True)
        self.output_data["Дата начала периода"] = pd.to_datetime(
            self.output_data["Дата начала периода"]
        )
        self.output_data["Дата окончания периода"] = pd.to_datetime(
            self.output_data["Дата окончания периода"]
        )
        self.output_data = self.output_data.reset_index(drop=True)
        self.output_data["№"] = self.output_data.index
        self.output_data["Дата уплаты процентов"] = self.output_data[
            "Дата уплаты процентов"
        ].apply(self.get_next_working_day)
        # здесь последняя дата уплаты процентов должна совпадать с погашением ОД

    def calculate_interest(self):
        self.output_data["Дата начала периода"] = pd.to_datetime(
            self.output_data["Дата начала периода"]
        )
        month_year_table = self.output_data["Дата начала периода"][0].strftime("%B %Y")

        if month_year_table == self.extract_file(self.data, self.start_date)[0]:
            new_row_xlsx = self.extract_file(self.data, self.start_date)[1]
            self.output_data_new = pd.concat(
                [self.output_data, new_row_xlsx], axis=1
            )  # Change to self.output_data_new
        else:
            new_row_xlsx = pd.DataFrame(
                {
                    "№": [0],
                    "Дата погашения Основного долга": 0,
                    "Сумма погашения Основного долга": 0,
                }
            )
            extract_file_new = pd.concat(
                [new_row_xlsx, self.extract_file(self.data, self.start_date)[1]],
                ignore_index=True,
            ).drop(columns="№")
            self.output_data_new = pd.concat(
                [self.output_data, extract_file_new], axis=1
            )  # Change to self.output_data_new
        self.output_data_new = self.output_data_new.fillna(0)
        self.output_data_new["Дата погашения Основного долга"] = self.output_data_new[
            "Дата погашения Основного долга"
        ].apply(lambda x: self.get_next_working_day(x) if x != 0 else 0)
        if (
            self.output_data_new.loc[0, "Дата погашения Основного долга"] == 0
        ):  # Change to self.output_data_new
            """ "делаем расчет для нулевой строки"""
            self.output_data_new.loc[0, "Дата окончания периода"] = (
                self.output_data_new.loc[0, "Дата начала периода"].replace(day=1)
                + pd.DateOffset(days=24)
            )
            self.output_data_new["Дата окончания периода"].apply(
                self.get_next_working_day
            )
            zero_line = (
                self.output_data_new.loc[0, "Дата окончания периода"]
                - self.output_data_new.loc[0, "Дата начала периода"]
            ).days
            self.output_data_new.loc[0, "Общая сумма процентов"] = round(
                (
                    self.output_data_new["Сумма погашения Основного долга"].sum()
                    * self.percent
                    / self.define_year(index=0)
                    * zero_line
                ),
                2,
            )
            self.output_data_new.loc[0, "Количество дней до погашения ОД"] = zero_line
            self.output_data_new.loc[0, "Остаток ОД на начало периода"] = round(
                self.output_data_new["Сумма погашения Основного долга"].sum(), 2
            )
            self.output_data_new.loc[0, "Количество дней после погашения ОД"] = 0
            self.output_data_new.loc[0, "Остаток ОД на конец периода"] = round(
                self.output_data_new["Сумма погашения Основного долга"].sum(), 2
            )
            self.output_data_new.loc[0, "Сумма процентов до погашения ОД"] = round(
                (
                    self.output_data_new["Сумма погашения Основного долга"].sum()
                    * self.percent
                    / self.define_year(index=0)
                    * zero_line
                ),
                2,
            )
            massive = 1
        else:
            massive = 0
        """"делаем расчет для всех остальных строк"""
        for i in range(massive, len(self.output_data_new)):
            """ "рассчитываем дату начала и  окончания периода"""
            self.output_data_new.loc[i, "Дата окончания периода"] = (
                self.output_data_new.loc[i, "Дата начала периода"].replace(day=1)
                + pd.DateOffset(days=24)
            )
            self.output_data_new["Дата окончания периода"] = self.output_data_new[
                "Дата окончания периода"
            ].apply(self.get_next_working_day)
            if (i - 1) <= -1:
                pass
            elif i == 0:
                self.output_data_new.loc[i, "Дата начала периода"] = (
                    self.output_data_new.loc[i, "Дата окончания периода"]
                    + pd.DateOffset(days=1)
                )
            else:
                self.output_data_new.loc[i, "Дата начала периода"] = (
                    self.output_data_new.loc[(i - 1), "Дата окончания периода"]
                    + pd.DateOffset(days=1)
                )
        for i in range(massive, len(self.output_data_new)):
            try:
                first_line_0_i = (
                    self.output_data_new.loc[i, "Дата погашения Основного долга"]
                    - self.output_data_new.loc[i, "Дата начала периода"]
                ).days + 1
                first_line_1_i = (
                    self.output_data_new.loc[i, "Дата окончания периода"]
                    - self.output_data_new.loc[i, "Дата погашения Основного долга"]
                ).days
            except:
                first_line_0_i = 0
                first_line_1_i = 0
            principal_debt_0_i = round(
                self.output_data_new["Сумма погашения Основного долга"].iloc[i:].sum(),
                2,
            )
            principal_debt_1_i = round(
                self.output_data_new["Сумма погашения Основного долга"]
                .iloc[(i + 1) :]
                .sum(),
                2,
            )
            principal_monthpay_0_i = round(
                principal_debt_0_i
                * self.percent
                / self.define_year(index=i)
                * first_line_0_i,
                2,
            )
            principal_monthpay_1_i = round(
                principal_debt_1_i
                * self.percent
                / self.define_year(index=i)
                * first_line_1_i,
                2,
            )

            self.output_data_new.loc[i, "Количество дней до погашения ОД"] = (
                first_line_0_i
            )
            self.output_data_new.loc[i, "Остаток ОД на начало периода"] = round(
                principal_debt_0_i, 2
            )
            self.output_data_new.loc[i, "Количество дней после погашения ОД"] = (
                first_line_1_i
            )
            self.output_data_new.loc[i, "Остаток ОД на конец периода"] = round(
                principal_debt_1_i, 2
            )
            self.output_data_new.loc[i, "Сумма процентов до погашения ОД"] = (
                principal_monthpay_0_i
            )
            self.output_data_new.loc[i, "Сумма процентов после погашения ОД"] = (
                principal_monthpay_1_i
            )
            self.output_data_new.loc[i, "Общая сумма процентов"] = round(
                principal_monthpay_0_i + principal_monthpay_1_i, 2
            )

        condition = (self.output_data_new["Сумма процентов до погашения ОД"] == 0) & (
            self.output_data_new["Сумма погашения Основного долга"] == 0
        )
        indices_to_drop = self.output_data_new.index[condition]
        self.output_data_new.drop(indices_to_drop, inplace=True)
        # делаем дату погашения % за последний месяц в дату погашения последнего ОД
        if self.output_data_new["Дата погашения Основного долга"].iloc[-1] == 0:
            self.output_data_new["Дата уплаты процентов"].iloc[-1] = (
                self.output_data_new["Дата погашения Основного долга"].iloc[-1]
            )
        elif self.output_data_new["Дата погашения Основного долга"].iloc[-1] != 0:
            self.output_data_new["Дата уплаты процентов"].iloc[-1] = (
                self.output_data_new["Дата погашения Основного долга"].iloc[-1]
            )

        self.output_data_new["Дата начала периода"] = self.output_data_new[
            "Дата начала периода"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        self.output_data_new["Дата окончания периода"] = self.output_data_new[
            "Дата окончания периода"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        self.output_data_new["Дата погашения Основного долга"] = self.output_data_new[
            "Дата погашения Основного долга"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        self.output_data_new["Дата уплаты процентов"] = self.output_data_new[
            "Дата уплаты процентов"
        ].apply(lambda x: x.strftime("%Y-%m-%d") if x != 0 else 0)
        # Save the updated output_data to an Excel file
        self.output_data_new.to_excel(
            "updated_output_data.xlsx", index=False
        )  # Change to self.output_data_new

    def start_function(self):
        self.create_dataframe()
        self.calculate_interest()
        return self.output_data_new


class MetallinvestBank(Bank):
    def __init__(self, data, interest_rate, date_of_issue, bank_day_percent):
        super().__init__(data, interest_rate, date_of_issue, bank_day_percent)

    @staticmethod
    def period_pay_percent_mib1():
        df1 = pd.read_excel(
            r"C:\Users\ШалапугинД\PycharmProjects\credit_project_learn_python\webapp\payment\Проценты МИБ1.xlsx"
        )
        return df1

    def create_dataframe(self, data):
        self.output_data = pd.DataFrame(
            {
                "№": range(0, self.extract_file(data, self.start_date)[3] + 1),
                "Дата погашения Основного долга": pd.date_range(
                    start=self.start_date,
                    periods=self.extract_file(data, self.start_date)[3] + 1,
                    freq="D",
                ),
                "Остаток ОД на начало периода": 0,
                "Сумма погашения Основного долга": 0,
                "Ставка банка, %": float(12.5),
                "Кол-во дней": 1,
                "Кол-во дней в году": 365,
                "Дата уплаты процентов": 0,
                "Общая сумма процентов": 0,
            }
        )
        # расчет для КД 8365-К
        self.output_data = self.output_data.reset_index(drop=True)
        self.output_data["№"] = self.output_data.index
        get_extract_file = self.extract_file(data, self.start_date)
        sum_od = get_extract_file[1]["Сумма погашения Основного долга"].sum()
        self.output_data.loc[0, "Остаток ОД на начало периода"] = round(sum_od, 2)
        self.output_data.loc[0, "Кол-во дней"] = 0
        df1 = (
            self.period_pay_percent_mib1()
        )  # Сохраняем результат выполнения функции period_pay_percent_mib1()
        df1["Дата уплаты процентов"] = df1["Дата уплаты процентов"].apply(
            lambda x: self.get_next_working_day(x) if x != 0 else 0
        )
        df1["Дата погашения Основного долга"] = df1[
            "Дата погашения Основного долга"
        ].apply(lambda x: self.get_next_working_day(x) if x != 0 else 0)
        # заполняем Остаток ОД
        self.output_data = self.output_data.drop(self.output_data.columns[0], axis=1)
        get1 = get_extract_file[1]
        merge_output_data = pd.merge(
            self.output_data,
            get1,
            on=["Дата погашения Основного долга"],
            how="left",
            suffixes=("_x", ""),
        )
        merge_output_data.drop(
            "Сумма погашения Основного долга_x", axis=1, inplace=True
        )
        merge_output_data = merge_output_data[
            [
                "Дата погашения Основного долга",
                "Остаток ОД на начало периода",
                "Сумма погашения Основного долга",
                "Ставка банка, %",
                "Кол-во дней",
                "Кол-во дней в году",
                "Дата уплаты процентов",
                "Общая сумма процентов",
            ]
        ]
        merge_bank_percent = pd.merge(
            merge_output_data,
            df1,
            on=["Дата погашения Основного долга"],
            how="left",
            suffixes=("_x", ""),
        )
        self.output_data = merge_bank_percent[
            [
                "Дата погашения Основного долга",
                "Остаток ОД на начало периода",
                "Сумма погашения Основного долга",
                "Ставка банка, %",
                "Кол-во дней",
                "Кол-во дней в году",
                "Дата уплаты процентов",
                "Общая сумма процентов",
            ]
        ]
        self.output_data = self.output_data.rename(
            columns={
                "Дата погашения Основного долга": "Дата начала периода",
                "Остаток ОД на начало периода": "Остаток основного долга",
            }
        )
        self.output_data["№"] = range(
            0, self.extract_file(data, self.start_date)[3] + 1
        )
        self.output_data = self.output_data[
            ["№"] + [col for col in self.output_data if col != "№"]
        ]
        self.output_data["Сумма погашения Основного долга"].fillna(0, inplace=True)

    def calculate_interest(self, data):
        self.output_data_new = self.output_data
        for i in range(1, self.extract_file(data, self.start_date)[3] + 1):
            ostatok_od_i = self.output_data_new.loc[(i - 1), "Остаток основного долга"]
            summary_pogash_i = self.output_data_new.loc[
                (i - 1), "Сумма погашения Основного долга"
            ]
            self.output_data_new.loc[i, "Остаток основного долга"] = (
                ostatok_od_i - summary_pogash_i
            )

        self.output_data_new["Кол-во дней в году"] = self.output_data_new[
            "Дата начала периода"
        ].apply(self.define_year_test)
        self.output_data_new["Ставка банка, %"] = self.output_data_new[
            "Дата начала периода"
        ].apply(get_nearest_interest_rate)
        self.output_data_new["Общая сумма процентов"] = self.output_data_new.apply(
            lambda row: float(row["Остаток основного долга"])
            * float(row["Ставка банка, %"])
            * float(row["Кол-во дней"])
            / float(row["Кол-во дней в году"]),
            axis=1,
        )
        self.output_data_new["Дата уплаты процентов"].fillna(0, inplace=True)
        print(self.output_data_new["Дата уплаты процентов"])
        # Создаем столбец 'Сумма %% итого' и заполняем его значениями
        cumulative_sum = 0
        for index, row in self.output_data_new.iterrows():
            if row["Дата уплаты процентов"] != 0:
                self.output_data_new.at[index, "Сумма %% нарастающим итогом"] = (
                    cumulative_sum + row["Общая сумма процентов"]
                )
                cumulative_sum = 0
            else:
                cumulative_sum += row["Общая сумма процентов"]
                self.output_data_new.at[index, "Сумма %% нарастающим итогом"] = (
                    cumulative_sum
                )

        self.output_data_new["Остаток основного долга"] = round(
            self.output_data_new["Остаток основного долга"], 2
        )
        self.output_data_new["Общая сумма процентов"] = round(
            self.output_data_new["Общая сумма процентов"], 2
        )
        self.output_data_new.to_excel("updated_output_data_МИБ1.xlsx", index=False)
        return self.output_data_new

    def start_function(self, data):
        self.create_dataframe(data)
        self.calculate_interest(data)
        return self.output_data_new
