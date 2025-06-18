import pytest
from pydantic import ValidationError

from app.api.schemas.answer import AnswerIn, AnswerOut

VALID_IN = {
    "ejercicio_id": 1,
    "answer": "42",
    "tiempo_seg": 10,
}


def test_answerin_valid():
    schema = AnswerIn(**VALID_IN)
    assert schema.ejercicio_id == 1
    assert schema.answer == "42"
    assert schema.tiempo_seg == 10


@pytest.mark.parametrize("field,value", [
    ("ejercicio_id", 0),                 # id no positivo
    ("ejercicio_id", -5),
    ("answer",   ""),                 # respuesta vacía
    ("answer",   "   "),
    ("tiempo_seg",  -1),                 # tiempo negativo
])
def test_answerin_invalid(field, value):
    data = VALID_IN.copy()
    data[field] = value
    with pytest.raises(ValidationError):
        AnswerIn(**data)


def test_answerout():
    out = AnswerOut(correcto=True)
    assert out.correcto is True
