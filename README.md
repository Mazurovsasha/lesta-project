# Flask REST API с PostgreSQL, Docker и CI/CD (Jenkins)

Этот проект представляет собой простое REST API на Flask для сохранения и получения результатов. Приложение упаковано в Docker и разворачивается с помощью CI/CD пайплайна на Jenkins.

## API Эндпоинты

| Метод | Путь       | Описание                                  |
|-------|------------|-------------------------------------------|
| GET   | /ping      | Проверка работоспособности сервиса (health-check). |
| POST  | /submit    | Принимает JSON и сохраняет его в БД.         |
| GET   | /results   | Возвращает все сохраненные записи из БД.    |

---

## 🚀 Как запустить проект локально

### Требования
* Docker
* Docker Compose
* [[Установка Docker](https://docs.docker.com/engine/install/ubuntu/)]

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
    Для локального запуска проекта используйте docker-compose-lokal.yml:

```bash
docker compose -f docker-compose-lokal.yml up --build -d
```

4.  **Готово!** Ваше приложение доступно по адресу http://localhost:5000.

---

## ⚙️ Примеры API-запросов

#### GET /ping

```bash
curl http://localhost:5000/ping
```

Ожидаемый ответ:

```json
{"status": "ok"}
```

#### POST /submit

```bash
curl -X POST http://localhost:5000/submit -H "Content-Type: application/json" -d '{"name": "Kirill", "score": 88}'
```

Ожидаемый ответ:

```json
{"id": 1, "message": "Result submitted successfully"}
```

#### GET /results

```bash
curl http://localhost:5000/results
```

Пример ответа:

```json
[{"id": 1, "name": "Kirill", "score": 88, "timestamp": "2025-06-07T11:44:09.729659"}]
```

---

## 🛠️ Настройка Jenkins

### Создание сети Jenkins

```bash
docker network create jenkins
```

### Запуск docker:dind контейнера

```bash
docker run --name jenkins-docker --rm --detach --privileged --network jenkins --network-alias docker \
  --env DOCKER_TLS_CERTDIR=/certs \
  --volume jenkins-docker-certs:/certs/client \
  --volume jenkins-data:/var/jenkins_home \
  --publish 2376:2376 \
  docker:dind --storage-driver overlay2
```

### Запуск Jenkins BlueOcean

```bash
docker run --name jenkins-blueocean --restart=on-failure --detach --network jenkins \
  --env DOCKER_HOST=tcp://docker:2376 \
  --env DOCKER_CERT_PATH=/certs/client \
  --env DOCKER_TLS_VERIFY=1 \
  --publish 8080:8080 --publish 50000:50000 \
  --volume jenkins-data:/var/jenkins_home \
  --volume jenkins-docker-certs:/certs/client:ro \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:latest
```

### Дополнительные шаги в контейнере Jenkins

```bash
docker exec jenkins-blueocean cat /var/jenkins_home/secrets/initialAdminPassword

docker exec -u 0 -it jenkins-blueocean /bin/bash
apt-get update && apt-get install -y docker.io sudo rsync pipx
usermod -aG docker jenkins
usermod -aG sudo jenkins
exit
docker restart jenkins-blueocean
```

---

## ⚙️ Как работает CI/CD

### Jenkins Pipeline

1. **Клонирование репозитория** из Git.
2. **Линтинг** с помощью flake8.
3. **Установка Docker и Compose** на удалённом сервере (при необходимости).
4. **Сборка Docker-образа**.
5. **Публикация образа** в Docker Hub.
6. **Развёртывание** на удалённый сервер (через `docker-compose`).

---

## 📦 Настройка CI/CD в Jenkins

### 1. Создание Pipeline Job

1.1 Перейдите в Jenkins UI → "Создать новый элемент".  
1.2 Введите имя проекта, выберите "Pipeline", нажмите "ОК".  
1.3 В секции Pipeline выберите: "Pipeline script from SCM".  
1.4 Укажите репозиторий и путь до `Jenkinsfile`.

### 2. Учетные данные

2.1 Перейдите в `Jenkins → Credentials`:  
- SSH-ключ для доступа к серверу (SSH Credentials).  
- Docker Hub логин/пароль (Username/Password).  
- Файл `.env` (Secret file).

### 3. Запуск Pipeline

3.1 Перед запуском можно передать параметр — IP-адрес хоста для деплоя.
3.2 После проверки кода линтеров, вам будет предложено изучить лог проверки и принять решение о продолжении деплоя.

---