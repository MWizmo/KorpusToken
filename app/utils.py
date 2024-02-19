def get_numeral_label(numeral: int, variants: dict) -> str:
    """Get label of a numeral according to the rules of the Russian language.

    :param numeral: number to label
    :param variants: dict with labeling variants: nominative, genitive_singular, genitive_plural
    :return: label
    """

    last_two_digits = numeral % 100

    if 11 <= last_two_digits <= 14:
        return variants['genitive_plural']

    last_digit = numeral % 10

    if last_digit == 1:
        return variants['nominative']

    if 2 <= last_digit <= 4:
        return variants['genitive_singular']

    return variants['genitive_plural']
