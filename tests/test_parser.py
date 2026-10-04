"""Тесты парсера командной строки."""
import pytest

from src.parser import tokenize, parse, ParseError


def test_empty_line():
    """Пустая строка даёт пустой список токенов."""
    assert tokenize("") == []


def test_simple_tokens():
    """Обычная строка делится по пробелам."""
    assert tokenize("ls -l /home") == ["ls", "-l", "/home"]


def test_double_quotes():
    """Двойные кавычки сохраняют пробелы внутри."""
    assert tokenize('ls "моя папка"') == ["ls", "моя папка"]


def test_single_quotes():
    """Одинарные кавычки сохраняют пробелы внутри."""
    assert tokenize("cd 'Мои документы'") == ["cd", "Мои документы"]


def test_adjacent_concat():
    """Соседние фрагменты склеиваются в один токен."""
    assert tokenize('ab"cd"ef') == ["abcdef"]


def test_escape_space():
    """Обратный слеш экранирует пробел."""
    assert tokenize(r"a\ b") == ["a b"]


def test_escape_quote():
    """Обратный слеш экранирует кавычку."""
    assert tokenize(r"\"x\"") == ['"x"']


def test_unclosed_quote():
    """Незакрытая кавычка приводит к ParseError."""
    with pytest.raises(ParseError):
        tokenize('ls "незакрытая')


def test_empty_quotes_token():
    """Пустые кавычки дают пустой токен."""
    assert tokenize('""') == [""]


def test_parse_returns_name_and_args():
    """parse возвращает (имя, список аргументов)."""
    assert parse('ls -l "a b"') == ("ls", ["-l", "a b"])


def test_parse_empty():
    """Пустая строка даёт (None, [])."""
    assert parse("   ") == (None, [])
