def is_good_table(table_data):

    if not table_data:
        return False

    if len(table_data) < 2:
        return False

    header = table_data[0]

    if not header:
        return False

    if len(header) < 2:
        return False

    valid_rows = 0

    for row in table_data[1:]:

        filled = sum(
            1 for cell in row
            if cell and str(cell).strip()
        )

        if filled >= max(1, len(header) // 2):
            valid_rows += 1

    return valid_rows > 0