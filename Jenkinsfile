pipeline {
    agent any

    environment {
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
                script {
                    // Установка необходимых пакетов для виртуального окружения
                    sh '''
                        apt-get update
                        apt-get install -y python3-venv python3-pip
                        
                        # Создаем виртуальное окружение и активируем его
                        python3 -m venv venv
                        source venv/bin/activate
                        pip install --upgrade pip
                        pip install flake8
                        flake8 .
                    '''
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
                    withCredentials([string(credentialsId: 'flask-env-secret', variable: 'ENV_CONTENT')]) {
                        sh """
                            echo "📦 Копируем docker-compose и деплоим на сервер..."

                            ssh -o StrictHostKeyChecking=no ${REMOTE_HOST} '
                                mkdir -p ${REMOTE_DIR}
                            '

                            rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" ./docker-compose.yml ${REMOTE_HOST}:${REMOTE_DIR}/

                            ssh ${REMOTE_HOST} 'echo "$ENV_CONTENT" > ${REMOTE_DIR}/.env'

                            ssh ${REMOTE_HOST} '
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
