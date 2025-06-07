pipeline {
    agent any

    environment {
        // Образы и хост
        IMAGE_NAME = 'mazurovsasha/flask-api'
        REMOTE_HOST = 'ubuntu@37.9.53.33'
        REMOTE_DIR = '/home/ubuntu/flask-api'

        // Jenkins credentials
        DOCKER_CREDENTIALS_ID = 'docker-credentials'
        SSH_CREDENTIALS_ID = 'ssh-remote-server'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    pip install flake8
                    flake8 .
                '''
            }
        }

        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        dockerImage.push("${BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to remote') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    withCredentials([string(credentialsId: 'flask-env-secret', variable: 'ENV_CONTENT')]) {
                        sh """
                            echo "🔧 Подключение и подготовка сервера..."

                            ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} '
                                set -e
                                # 1. Создание директории
                                mkdir -p ${REMOTE_DIR}

                                # 2. Установка Docker
                                if ! command -v docker >/dev/null 2>&1; then
                                    echo "🚀 Устанавливаем Docker..."
                                    curl -fsSL https://get.docker.com -o get-docker.sh
                                    sh get-docker.sh
                                    sudo usermod -aG docker \$USER
                                else
                                    echo "✅ Docker уже установлен"
                                fi

                                # 3. Установка Docker Compose
                                if ! command -v docker-compose >/dev/null 2>&1; then
                                    echo "🚀 Устанавливаем Docker Compose..."
                                    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)" -o docker-compose
                                    chmod +x docker-compose
                                    sudo mv docker-compose /usr/local/bin/docker-compose
                                else
                                    echo "✅ Docker Compose уже установлен"
                                fi
                            '

                            echo "📦 Копируем docker-compose.yml"
                            rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" ./docker-compose.yml ${REMOTE_HOST}:${REMOTE_DIR}/

                            echo "🔐 Обновляем .env из Jenkins Secrets"
                            ssh ${REMOTE_HOST} 'echo "$ENV_CONTENT" > ${REMOTE_DIR}/.env'

                            echo "🚀 Запускаем docker-compose"
                            ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} '
                                cd ${REMOTE_DIR} &&
                                docker-compose down || true &&
                                docker-compose pull &&
                                docker-compose up -d --remove-orphans
                            '
                        """
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
