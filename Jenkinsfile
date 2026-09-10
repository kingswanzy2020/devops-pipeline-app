pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "ahmed3015/devops-pipeline-app"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
                sh "docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }
        stage('Update Manifests') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh """
                        rm -rf devops-pipeline-manifests
                        git clone https://\${GIT_USER}:\${GIT_TOKEN}@github.com/\${GIT_USER}/devops-pipeline-manifests.git
                        cd devops-pipeline-manifests
                        sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|' k8s/deployment.yaml
                        git config user.email "jenkins@pipeline.local"
                        git config user.name "Jenkins CI"
                        git add .
                        git commit -m "Update image to build ${BUILD_NUMBER}"
                        git push origin main
                    """
                }
            }
        }
    }

    post {
        always {
            sh "docker logout || true"
        }
    }
}        