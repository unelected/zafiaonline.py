# zafiaonline.py (Fork)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)

## Описание
Этот проект является форком оригинальной библиотеки [mafiaonline.py](https://github.com/Zakovskiy/mafiaonline.py), которая предоставляет API для взаимодействия с [Мафией Онлайн](https://play.google.com/store/apps/details?id=com.tokarev.mafia). 
Форк был создан для добавления нового функционала и исправления некоторых ошибок, а также для улучшения чтения кода.

### Основные изменения по сравнению с оригинальной библиотекой:
- **Исправления**: Небольшие исправления (переименование Renamers в Renaming и str, enum в StrEnum. и тп)
- **Оптимизация**: вырезаны ненужные импорты либы, (socks -- временно вырезано)
(все изменения были закоментированны, чтобы при желании было проще сменить функции в исходный стиль

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
