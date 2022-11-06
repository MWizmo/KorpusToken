from app import app
import xlsxwriter
import os


def generate_weekly_voting_xlsx(table_name: str, weekly_results: list) -> None:
    workbook_path = os.path.join(app.root_path + '/static/weekly_votings/', table_name)
    if os.path.isfile(workbook_path):
        return None

    workbook = xlsxwriter.Workbook(workbook_path)

    header_cell_border = workbook.add_format()
    header_cell_border.set_bottom()
    header_cell_border.set_right()
    row_cell_border = workbook.add_format()
    row_cell_border.set_bottom()
    last_row_cell_border = workbook.add_format()
    last_row_cell_border.set_bottom()
    last_row_cell_border.set_right()

    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Название проекта', header_cell_border)
    worksheet.write('B1', 'Участник команды', header_cell_border)
    worksheet.write('C1', 'Движение', header_cell_border)
    worksheet.write('D1', 'Завершенность', header_cell_border)
    worksheet.write('E1', 'Подтверждение средой', header_cell_border)

    max_text_len = len('Подтверждение средой')
    current_row = 2
    for result in weekly_results:
        worksheet.write(f"A{current_row}", result['team'], row_cell_border)
        for i in range(1, 4):
            worksheet.write(current_row - 1, i, "", row_cell_border)
        worksheet.write(f"E{current_row}", "", last_row_cell_border)
        current_row += 1
        for member in result['marks']:
            worksheet.write(f"A{current_row}", "", row_cell_border)
            worksheet.write(f"B{current_row}", member['name'], row_cell_border)
            worksheet.write(f"C{current_row}", member['marks1'][0], row_cell_border)
            worksheet.write(f"D{current_row}", member['marks2'][0], row_cell_border)
            worksheet.write(f"E{current_row}", member['marks3'][0], last_row_cell_border)
            max_text_len = len(member['name']) if max_text_len < len(member['name']) else max_text_len
            current_row += 1
        max_text_len = len(result['team']) if max_text_len < len(result['team']) else max_text_len

    worksheet.freeze_panes(1, 0)
    worksheet.set_column(0, 4, max_text_len + 2)
    worksheet.set_default_row(15)
    worksheet.set_row(0, 30)

    workbook.close()
