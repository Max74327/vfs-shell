"""Парсер командной строки с поддержкой кавычек и экранирования."""
from dataclasses import dataclass, field

SPACE_CHARS = (" ", "\t")
BACKSLASH = "\\"
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'


class ParseError(Exception):
    """Ошибка разбора командной строки."""


@dataclass
class State:
    """Состояние парсера при посимвольном обходе строки."""

    tokens: list = field(default_factory=list)
    buf: list = field(default_factory=list)
    in_single: bool = False
    in_double: bool = False
    escape: bool = False
    started: bool = False


def _flush(state: State) -> None:
    """Сохраняет накопленный буфер как отдельный токен."""
    if state.started:
        state.tokens.append("".join(state.buf))
        state.buf.clear()
        state.started = False


def _on_escape(state: State, ch: str) -> None:
    """Обрабатывает символ, экранированный обратным слешем."""
    state.buf.append(ch)
    state.escape = False
    state.started = True


def _on_quote(state: State, ch: str) -> None:
    """Переключает флаг одинарных или двойных кавычек."""
    if ch == SINGLE_QUOTE and not state.in_double:
        state.in_single = not state.in_single
    else:
        state.in_double = not state.in_double
    state.started = True


def _on_space(state: State) -> None:
    """Завершает текущий токен при встрече разделителя."""
    _flush(state)


def _on_char(state: State, ch: str) -> None:
    """Добавляет обычный символ в текущий токен."""
    state.buf.append(ch)
    state.started = True


def _handle(state: State, ch: str) -> None:
    """Маршрутизирует один символ в соответствующий обработчик."""
    if state.escape:
        _on_escape(state, ch)
        return
    if ch == BACKSLASH and not state.in_single:
        state.escape = True
        state.started = True
        return
    if ch in (SINGLE_QUOTE, DOUBLE_QUOTE):
        _on_quote(state, ch)
        return
    if ch in SPACE_CHARS and not state.in_single \
            and not state.in_double:
        _on_space(state)
        return
    _on_char(state, ch)


def _finalize(state: State) -> list:
    """Проверяет корректность состояния и возвращает токены."""
    if state.escape:
        state.buf.append(BACKSLASH)
    if state.in_single or state.in_double:
        raise ParseError("unterminated quote")
    _flush(state)
    return state.tokens


def tokenize(line: str) -> list:
    """
    Разбивает строку на аргументы.

    Правила:
      * пробелы и табы разделяют аргументы вне кавычек;
      * одинарные и двойные кавычки сохраняют содержимое как один токен;
      * обратный слеш экранирует следующий символ;
      * соседние фрагменты склеиваются: ab"cd"ef -> abcdef;
      * незакрытая кавычка приводит к ParseError.
    """
    state = State()
    for ch in line:
        _handle(state, ch)
    return _finalize(state)


def parse(line: str):
    """
    Возвращает пару (имя команды, аргументы).

    Для пустой строки или строки из пробелов — (None, []).
    """
    tokens = tokenize(line)
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]
