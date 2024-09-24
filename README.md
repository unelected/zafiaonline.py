# zafiaonline.py
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Fork](https://img.shields.io/github/forks/Zakovskiy/mafiaonline.py)

## Описание
Этот проект является форком оригинальной библиотеки [mafiaonline.py](https://github.com/Zakovskiy/mafiaonline.py), которая предоставляет API для взаимодействия с [Мафией Онлайн](https://play.google.com/store/apps/details?id=com.tokarev.mafia). Форк был создан для добавления нового функционала и исправления некоторых ошибок, а также для улучшения чтения кода.

### Основные изменения по сравнению с оригинальной библиотекой:
- **Исправления**: Небольшие исправления, как переименование Renamers в Renaming и str, enum в StrEnum.
- **Оптимизация производительности**: (socket) -- вырезанная часть либы, т.к. не используются
socks -- вырезанно, так как я не использую прокси

## Установка

``` bash
git clone https://github.com/unelected/zafiaonline.py.git
```

# Пример использования

```python
import zafiaonline

Mafia = zafiaonline.Client()
Mafia.sign_in("email", "password")
```
