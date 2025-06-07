# Flask REST API с PostgreSQL, Docker и CI/CD (Jenkins)

Этот проект представляет собой простое REST API на Flask для сохранения и получения результатов. Приложение упаковано в Docker и разворачивается с помощью CI/CD пайплайна на Jenkins.

## API Эндпоинты

| Метод | Путь       | Описание                                  |
|-------|------------|-------------------------------------------|
| GET   | /ping    | Проверка работоспособности сервиса (health-check).   |
| POST  | /submit  | Принимает JSON и сохраняет его в БД.         |
| GET   | /results | Возвращает все сохраненные записи из БД.  |

---

## 🚀 Как запустить проект локально

### Требования
* Docker
* Docker Compose

### Инструкция по запуску
1.  **Клонируйте репозиторий:**

```bash
    git clone <URL вашего репозитория>
    cd flask-api
```

2.  **Создайте и заполните .env файл:**
    Скопируйте .env.example в новый файл .env и при необходимости измените значения.

```bash
    cp .env.example .env
```

3.  **Соберите и запустите контейнеры:**
    Для локального запуска проекта используйте docker-compose-lokal.yml
    Эта команда соберет образ для Flask-приложения и запустит его вместе с базой данных PostgreSQL.

```bash
    docker compose -f docker-compose-lokal.yml up --build -d
```

4.  **Готово!** Ваше приложение доступно по адресу http://localhost:5000.

---

## ⚙️ Примеры API-запросов

#### GET /ping
Проверка статуса.

```bash
curl http://localhost:5000/ping
```

Ожидаемый ответ:

```JSON
{"status":"ok"}
```

#### POST /submit

```bash
curl -X POST http://localhost:5000/submit -H "Content-Type: application/json" -d '{"name": "Kirill", "score": 88}'
```

Ожидаемый ответ:

```JSON
{"id":1,"message":"Result submitted successfully"}
```

#### GET /results

```bash
curl http://localhost:5000/results
```

Пример ответа:

```JSON
[{"id":1,"name":"Kirill","score":88,"timestamp":"2025-06-07T11:44:09.729659"}]
```

## Настройка контейнера с Jenkins

```bash
docker network create jenkins

docker run \
  --name jenkins-docker \
  --rm \
  --detach \
  --privileged \
  --network jenkins \
  --network-alias docker \
  --env DOCKER_TLS_CERTDIR=/certs \
  --volume jenkins-docker-certs:/certs/client \
  --volume jenkins-data:/var/jenkins_home \
  --publish 2376:2376 \
  docker:dind \
  --storage-driver overlay2


docker run \
  --name jenkins-blueocean \
  --restart=on-failure \
  --detach \
  --network jenkins \
  --env DOCKER_HOST=tcp://docker:2376 \
  --env DOCKER_CERT_PATH=/certs/client \
  --env DOCKER_TLS_VERIFY=1 \
  --publish 8080:8080 \
  --publish 50000:50000 \
  --volume jenkins-data:/var/jenkins_home \
  --volume jenkins-docker-certs:/certs/client:ro \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:latest


docker exec jenkins-blueocean cat /var/jenkins_home/secrets/initialAdminPassword

docker exec -u 0 -it jenkins-blueocean /bin/bash
apt-get update
apt-get install -y docker.io
usermod -aG docker jenkins
apt-get update
apt-get install sudo
usermod -aG sudo jenkins
apt-get install pipx
apt-get install rsync
exit
docker restart jenkins-blueocean
```

## Как работает CI/CD

### 1. **Jenkins Pipeline**

Процесс автоматической сборки и развертывания проекта на сервере с использованием Jenkins:

1. **Скачивание репозитория**: Код проекта клонируется из Git-репозитория.
2. **Запуск линтинга**: Код проверяется с использованием flake8 на наличие синтаксических ошибок.
3. **Установка Docker и Docker Compose на удаленный сервер**: Jenkins проверяет, установлен ли Docker и Docker Compose на удаленном сервере. Если нет, то они устанавливаются автоматически.
4. **Сборка Docker-образа**: Docker-образ для Flask-приложения собирается на основе Dockerfile.
5. **Публикация в Docker Hub**: Новый образ загружается в Docker Hub.
6. **Развертывание на удаленный сервер**: На удаленном сервере выполняются команды для обновления контейнеров через Docker Compose.

Процесс автоматизирует развертывание Flask-приложения, начиная с линтинга, сборки и до публикации и развертывания на удаленном сервере.


## Как настроить CI/CD в Jenkins

1. Убедитесь, что у вас есть установленные и настроенные Jenkins и Docker.
2. Создайте новый pipeline job в Jenkins и настройте его, чтобы он использовал ваш репозиторий.
3. В Jenkinsfile определите этапы, как показано в примере выше, для CI/CD процесса.


## Пошаговая настройка Jenkins Pipeline

### 2. Создание нового Pipeline Job в Jenkins

2.1 Зайдите в Jenkins UI и нажмите "Создать новый элемент". 
2.2 Введите имя для проекта, выберите "Pipeline" и нажмите "Ок".
2.3 В разделе "Pipeline" выберите "Pipeline script from SCM" и настройте репозиторий с вашим проектом. Укажите Git репозиторий и путь к Jenkinsfile.

### 3. Добавление секретов и учетных данных в Jenkins

3.1 Перейдите в "Jenkins > Учетные данные" и добавьте секреты и SSH ключи для аутентификации:
   - Для Docker Hub: Добавьте учетные данные в раздел "Docker Credentials".
   - Для SSH доступа: Добавьте ключ SSH для удаленного сервера в разделе "SSH Credentials".
   - Для файла .env: Добавьте его как "Secret File" в разделе "Jenkins Credentials".

### 4. Конфигурация Pipeline

4.1 В Jenkinsfile используйте `withCredentials` для подключения к этим секретам, как показано в примере.
4.2 Настройте шаги пайплайна: проверку, сборку, пуш и деплой.


## Заключение

Теперь ваш проект настроен на использование CI/CD пайплайна в Jenkins. Он будет автоматически собирать, публиковать и развертывать ваш проект, обеспечивая высокую степень автоматизации при разработке и развертывании Flask-приложения.
