import pygsheets

gc = pygsheets.authorize(service_file='timetable-bot')


def re_str(number):
    string = ''
    for i in number:
        if i.isdigit():
            string += i
    return string


def re_num(string):
    number = ''
    for i in string:
        if not i.isdigit():
            number += i
    return number


class Sheets:

    def __init__(self, doc, user_id):
        self.doc = gc.open(doc)
        self.wks = self.doc.worksheet('title', f'{user_id}')

    def update_sheet_info(self, day_of_week, cells_list):
        colonka = self.wks.find(f'{day_of_week}')[0].address.label
        bukva = re_num(colonka)
        self.wks.clear(start=f'{bukva}2', end=f'{bukva}50')
        self.wks.update_values_batch([f'{bukva}2:{bukva}{len(cells_list)+2}'], [[cells_list]], 'COLUMNS')


    def show_table_info(self, day_of_week):
        colonka = self.wks.find(f'{day_of_week}')[0].address.label
        info = self.wks.get_values(f'{colonka}', f'{colonka}9')
        return info
