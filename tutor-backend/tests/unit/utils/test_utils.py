import pytest
from src.utils.utils import strip_and_lower

@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("  HELLO  ", "hello"),                  # recorta y pasa a minúsculas
        ("\tMiXeD CaSe\n", "mixed case"),        # espacios y tab/newline
        (" already clean ", "already clean"),    # recorta, deja minúsculas
        ("ALLLOWER", "alllower"),                # sin espacios, solo mayúsculas
        ("   ", ""),                             # solo espacios → cadena vacía
        ("", ""),                                # ya vacía
        ("  ÚNÍCÓ   ", "únícó"),                 # caracteres Unicode
    ]
)
def test_strip_and_lower_varios_casos(input_str, expected):
    assert strip_and_lower(input_str) == expected

def test_strip_and_lower_no_mutate_original():
    s = "  AbC  "
    _ = strip_and_lower(s)
    # la cadena original no debe cambiar
    assert s == "  AbC  "

def test_strip_and_lower_attr_error_on_non_str():
    # Pasa algo que no es str → AttributeError
    with pytest.raises(AttributeError):
        strip_and_lower(None)  # intenta hacer None.strip()

    with pytest.raises(AttributeError):
        strip_and_lower(123)   # intenta hacer int.strip()
