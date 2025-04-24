import sys
import traceback
from src.bot import run_bot

if __name__ == "__main__":
    try:
        print("Запуск бота из main.py...")
        run_bot()
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        traceback.print_exc()
        sys.exit(1)