# Используем стабильный Python 3.11
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y build-essential

# Копируем проект в контейнер
WORKDIR /app
COPY . .

# Устанавливаем Python-библиотеки
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Запускаем бота
CMD ["python", "bot.py"]
