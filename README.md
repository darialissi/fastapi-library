### RESTful API для управления каталогом библиотеки

#### [Техническое задание](./spec.md)

#### UML диаграмма SQL базы данных
![UML диаграмма](UmlDiagram.png)

#

#### Запуск приложения при помощи Docker

- git clone https://github.com/darialissi/fastapi-library.git

- cd fastapi-library && docker-compose up
#

Документация доступна на http://127.0.0.1:8000/docs 

![Swagger-1](docs-1.png)
![Swagger-2](docs-2.png)

#

#### Тестирование

1. Поднимаем postgres и redis
   
   **docker-compose --file docker-compose.local-tests.yml up -d**

2. Устанавливаем poetry

   **pip install poetry**

3. Подтягиваем зависимости
   
   **poetry install**

4. Запускаем pytest
   
   **poetry run pytest**