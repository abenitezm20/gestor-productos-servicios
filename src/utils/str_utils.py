import re


def str_none_or_empty(var: str) -> bool:
    """
    Valida si una cadena de texto es nula o vacía
    """
    return not var or len(var) == 0


def is_email(email: str) -> bool:
    """
    Valida si una cadena de texto es un correo electrónico válido
    """
    regex = r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    match = re.fullmatch(regex, email)
    return match is not None
