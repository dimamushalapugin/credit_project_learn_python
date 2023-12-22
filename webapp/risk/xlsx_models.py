class XlsxCreator:
    def __init__(self, sheet):
        self.sheet = sheet

    def __repr__(self):
        return f'XLSX FILE. Активный лист: {self.sheet.title}'

    def is_cell_none(self, cell):
        return self.sheet[cell].value is None

    def get_cell(self, cell):
        if self.is_cell_none(cell):
            return ''
        else:
            cell_value = self.sheet[cell].value
            return str(cell_value).strip() if cell_value is not None else ''

    def set_cell(self, cell, value):
        self.sheet[cell] = value
