### RESTful API для управления каталогом библиотеки

#### [Техническое задание](./spec.md)

#### UML диаграмма SQL базы данных
![UML диаграмма](UmlDiagram.png)

#

#### Запуск приложения при помощи Docker (docker compose v2)


1. Клонируем репозиторий
   
   ```
   git clone https://github.com/darialissi/fastapi-library.git
   ```
2. Переходим в директорию проекта и запускаем
   
   ```
   cd fastapi-library && docker compose --profile prod up
   ```
#

Документация доступна на *http://127.0.0.1:8000/docs*

![Swagger-1](docs-1.png)
![Swagger-2](docs-2.png)

#

#### Логи приложения

```
docker exec app_prod cat server.log
```
#


#### Тестирование

1. Поднимаем postgres и redis в тестовом окружении
   
   ```
   docker compose --profile test up -d
   ```

2. Устанавливаем poetry

   ```
   pip install poetry
   ```

3. Подтягиваем зависимости
   
   ```
   poetry install --no-root
   ```

4. Запускаем pytest
   
   ```
   poetry run pytest
   ```