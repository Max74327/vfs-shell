#!/usr/bin/env bash
#
# Скрипт запуска эмулятора VFS Shell.
#
# Использование:
#   ./run.sh            # запустить GUI
#   ./run.sh cli        # запустить консольный режим
#   ./run.sh test       # запустить тесты (pytest)
#   ./run.sh lint       # проверить PEP8 (pycodestyle)
#   ./run.sh clean      # удалить служебные файлы
#   ./run.sh help       # справка

set -euo pipefail

PYTHON="${PYTHON:-python3}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

usage() {
    cat <<EOF
Использование: ./run.sh [команда]

Команды:
  (без аргумента)  запустить GUI
  cli              запустить консольный режим
  test             запустить тесты (pytest)
  lint             проверить PEP8 (pycodestyle, max-line-length=80)
  clean            удалить __pycache__ и .pytest_cache
  help             показать эту справку
EOF
}

run_gui() {
    exec "$PYTHON" -m src.main
}

run_cli() {
    exec "$PYTHON" -m src.main --cli
}

run_tests() {
    exec "$PYTHON" -m pytest -q tests
}

run_lint() {
    exec "$PYTHON" -m pycodestyle --max-line-length=80 src tests
}

run_clean() {
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    echo "Очищено."
}

main() {
    local cmd="${1:-}"
    case "$cmd" in
        "")      run_gui ;;
        cli)     run_cli ;;
        test)    run_tests ;;
        lint)    run_lint ;;
        clean)   run_clean ;;
        help|-h|--help) usage ;;
        *)
            echo "Неизвестная команда: $cmd" >&2
            usage >&2
            exit 1
            ;;
    esac
}

main "$@"
