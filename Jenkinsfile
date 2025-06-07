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
                    sh 'pip install --user flake8'
                        
                    sh 'flake8 . > flake8.log || tru'    
        
                }
            }
            post {
                always {
                    // Архивируем лог файл flake8.log
                    archiveArtifacts artifacts: '**/flake8.log', allowEmptyArchive: true
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
