pipeline {
    agent any

    parameters {
        string(name: 'REMOTE_HOST_IP', defaultValue: '37.9.53.33', description: 'Введите IP-адрес удаленного хоста, на который требуется установить приложение')
    }

    environment {
        IMAGE_NAME = 'mazurovsasha/flask-api'
        REMOTE_HOST = "ubuntu@{params.REMOTE_HOST_IP}"
        REMOTE_DIR = 'flask-api'

        // Jenkins credentials
        DOCKER_CREDENTIALS_ID = 'docker-credentials-id'
        SSH_CREDENTIALS_ID = 'ssh-remote-server'
        SECRETS_FILE_ID = 'flask-secrets-file' 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                script {
                    // Выполняем линтинг и сохраняем вывод в файл
                    sh 'flake8 . > flake8.log || true'    
                }
            }
            post {
                always {
                    // Архивируем лог файл flake8.log
                    archiveArtifacts artifacts: '**/flake8.log', allowEmptyArchive: true
                }
            }
        }

        stage('Install Docker and Docker Compose on Remote Server') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    script {
                        sh """
                            echo '📦 Проверяем и устанавливаем Docker и Docker Compose на сервере...'

                            ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} '
                                # Устанавливаем Docker
                                if ! command -v docker &> /dev/null; then
                                    echo "Docker не установлен. Устанавливаем..."
                                    sudo apt-get update &&
                                    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common &&
                                    curl -fsSL https://get.docker.com -o get-docker.sh &&
                                    sudo sh get-docker.sh &&
                                    sudo systemctl start docker &&
                                    sudo systemctl enable docker &&
                                    echo "Docker успешно установлен"
                                else
                                    echo "Docker уже установлен"
                                fi

                                # Устанавливаем Docker Compose
                                if ! command -v docker-compose &> /dev/null; then
                                    echo "Docker Compose не установлен. Устанавливаем..."
                                    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose &&
                                    sudo chmod +x /usr/local/bin/docker-compose &&
                                    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose &&
                                    echo "Docker Compose успешно установлен"
                                else
                                    echo "Docker Compose уже установлен"
                                fi
                            '
                        """
                    }
                }
            }
        }

        stage('Build Docker image') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        dockerImage.push("${BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Remote Server') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    withCredentials([file(credentialsId: SECRETS_FILE_ID, variable: 'SECRET_FILE')]) {
                        script {
                            sh """
                                echo "📦 Копируем необходимые файлы и деплоим на сервер..."

                                # Создаем директорию, если её нет
                                ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} 'sudo -u ubuntu mkdir -p ~/${REMOTE_DIR}'
                                ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} 'sudo -u ubuntu mkdir -p ~/${REMOTE_DIR}/migrations'

                                # Копируем docker-compose.yml на сервер
                                rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" ./docker-compose.yml ${REMOTE_HOST}:${REMOTE_DIR}/

                                # Копируем директорию migrations на сервер 
                                rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" ./migrations/ ${REMOTE_HOST}:${REMOTE_DIR}/migrations/

                                # Передаем секретный файл (с .env) на сервер
                                scp -o StrictHostKeyChecking=no $SECRET_FILE ${REMOTE_HOST}:${REMOTE_DIR}/.env

                                # Выполняем деплой с использованием Docker Compose
                                ssh ${REMOTE_HOST} '
                                    source ${REMOTE_DIR}/.env &&
                                    cd ${REMOTE_DIR} &&
                                    sudo docker-compose down || true &&
                                    sudo docker-compose pull &&
                                    sudo docker-compose up -d --remove-orphans
                                '
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
