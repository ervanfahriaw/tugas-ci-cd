pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        REGISTRY_NAME = 'python-crud-api'
        CONTAINER_NAME = 'production-api-container'
        PORT_MAPPING = '5000:5000'
        VOLUME_NAME = 'production-api-data'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('2. Code Syntax & Automated Tests') {
            steps {
                echo 'Running Python syntax verification and unit tests...'
                sh '''
                if command -v python3 >/dev/null 2>&1; then
                    python3 -m py_compile app.py
                    python3 -m unittest test_app.py
                else
                    echo "Python3 not in Jenkins agent directly; running tests inside python:3.11-slim container..."
                    docker run --rm -v "$(pwd)":/app -w /app python:3.11-slim sh -c "python -m py_compile app.py && python -m unittest test_app.py"
                fi
                '''
            }
        }

        stage('3. Build Docker Image') {
            steps {
                script {
                    def shortCommit = sh(script: "git rev-parse --short HEAD || echo local", returnStdout: true).trim()
                    echo "Building Docker image with build number ${BUILD_NUMBER} and commit SHA ${shortCommit}..."
                    sh "docker build -t ${REGISTRY_NAME}:${BUILD_NUMBER} ."
                    sh "docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:latest"
                    sh "docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:${shortCommit}"
                }
            }
        }

        stage('4. Automated Deployment') {
            steps {
                sh '''
                echo "Stopping and removing existing container if present..."
                docker stop ${CONTAINER_NAME} || true
                docker rm ${CONTAINER_NAME} || true
                echo "Ensuring named volume exists for data persistence..."
                docker volume create ${VOLUME_NAME}
                echo "Starting production container with named volume on jenkins-net network..."
                docker run -d \
                  --name ${CONTAINER_NAME} \
                  --network jenkins-net \
                  -p ${PORT_MAPPING} \
                  -v ${VOLUME_NAME}:/var/lib/backend_data \
                  --restart unless-stopped \
                  ${REGISTRY_NAME}:latest
                '''
            }
        }

        stage('5. Health Check') {
            steps {
                echo 'Waiting for container application startup...'
                sh 'sleep 3'
                echo 'Performing automated HTTP health check...'
                sh '''
                curl -fsS http://${CONTAINER_NAME}:5000/health || curl -fsS http://localhost:5000/health
                '''
                echo 'Displaying recent container runtime logs...'
                sh 'docker logs --tail 20 ${CONTAINER_NAME}'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. Deployment is healthy and active.'
        }
        failure {
            echo 'Pipeline failed. Inspect Console Output for diagnostics.'
        }
    }
}
