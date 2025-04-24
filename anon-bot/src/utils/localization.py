from ..config.settings import MESSAGES

class Localization:
    @staticmethod
    def get(key, **kwargs):
        """Получает локализованное сообщение по ключу с подстановкой параметров"""
        keys = key.split('.')
        value = MESSAGES
        for k in keys:
            value = value.get(k, {})
        return value.format(**kwargs) if isinstance(value, str) else str(value) 