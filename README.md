# Candy-Delivery-App
Backend implementation of candy delivery app "Сласти от всех напастей"

### Deployment

#### Initial
 - Install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/)
 - Clone the repository
 ```console
bzvr@remote:~$ sudo apt install git
bzvr@remote:~$ git clone https://github.com/bzvr/Candy-Delivery-App
bzvr@remote:~$ cd Candy-Delivery-App/
```

#### Development mode
1. Build and run 
 ```console
bzvr@remote:~/Candy-Delivery-App$ sudo docker-compose up --build
```
2. Stop the containers and remove (-v) the volumes along with the containers.
 ```console
bzvr@remote:~/Candy-Delivery-App$ sudo docker-compose down -v
```


#### Production mode

1.  Create a env.prod file and put the content of the file env.dev there, replacing credentials with more secure ones.

 ```console
bzvr@remote:~/Candy-Delivery-App$ vim env.prod
bzvr@remote:~/Candy-Delivery-App$ cat env.prod
```

```
SECRET_KEY=*******

POSTGRES_ENGINE=django.db.backends.postgresql_psycopg2
POSTGRES_DB=candy_delivery
POSTGRES_USER=candy_admin
POSTGRES_PASSWORD=*******
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

DJANGO_ADMIN_USERNAME=admin
DJANGO_ADMIN_PASSWORD=*******
```

2. Build and run 
 ```console
bzvr@remote:~/Candy-Delivery-App$ sudo docker-compose -f docker-compose.prod.yml up -d --build
```



#### Requirements
```python3
Package     			Version

Django      			3.1.7
djangorestframework             3.11.0
django-restapi 			0.1.3
psycopg2-binary     	        2.8.5
redis       			3.5.3
gunicorn      			20.1.0
python-dateutil    		2.22.0

```

#### Additional tasks

| Check   |  Task
|---------|---
| ☑       |  Наличие реализованного обработчика 6: GET /couriers/$courier_id
| ☑       |  Наличие структуры с подробным описанием ошибок каждого некорректного поля, пришедшего в запросе
| ☑       |  Явно описанные внешние python-библиотеки (зависимости)
| ☐       |  Наличие тестов
| ☑       |  Наличие файла README в корне репозитория с инструкциями по установке, развертыванию и запуску сервиса и тестов
| ☐/☑     |  Автоматическое возобновление работы REST API после перезагрузки виртуальной машины
| ☑       |  Возможность обработки нескольких запросов сервисом одновременно

