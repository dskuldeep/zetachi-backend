pipeline {
    agent any

    environment {
        // Docker image and EC2 instance details
        IMAGE_NAME = 'dskuldeep/zetachi-backend'
        AWS_EC2_IP = 'ec2-174-129-135-170.compute-1.amazonaws.com'
        SSH_CREDENTIALS = 'Kuldeep-Access'
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials-id'
        DOCKER_HOST = 'tcp://174.129.135.170:2375' // Remote Docker daemon
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/dskuldeep/zetachi-backend.git', credentialsId: '438bf32e-3b5e-4512-9c92-5eeca959630c'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image using remote Docker daemon
                    withEnv(["DOCKER_HOST=${env.DOCKER_HOST}"]) {
                        dockerImage = docker.build("${env.IMAGE_NAME}")
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Push Docker image to DockerHub
                    withCredentials([usernamePassword(credentialsId: env.DOCKERHUB_CREDENTIALS, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        withEnv(["DOCKER_HOST=${env.DOCKER_HOST}"]) {
                            docker.withRegistry('https://index.docker.io/v1/', env.DOCKERHUB_CREDENTIALS) {
                                dockerImage.push("${env.BUILD_NUMBER}")
                                dockerImage.push('latest')
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    sshagent([env.SSH_CREDENTIALS]) {
                        withCredentials([string(credentialsId: 'DATABASE_URL', variable: 'DATABASE_URL'),
                                        string(credentialsId: 'SECRET_KEY', variable: 'SECRET_KEY'),
                                        string(credentialsId: 'ACCESS_TOKEN_EXPIRE_MINUTES', variable: 'ACCESS_TOKEN_EXPIRE_MINUTES'),
                                        string(credentialsId: 'REFRESH_TOKEN_EXPIRE_DAYS', variable: 'REFRESH_TOKEN_EXPIRE_DAYS'),
                                        string(credentialsId: 'GROQ_API_KEY', variable: 'GROQ_API_KEY'),
                                        string(credentialsId: 'AWS_ACCESS_KEY', variable: 'AWS_ACCESS_KEY'),
                                        string(credentialsId: 'AWS_SECRET_KEY', variable: 'AWS_SECRET_KEY')]) {
                            sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${env.AWS_EC2_IP} << 'EOF'
                            if [ "$(docker ps -aq -f name=fastapi_app)" ]; then
                                sudo docker stop fastapi_app
                                sudo docker rm fastapi_app
                            fi
                            sudo docker pull ${env.IMAGE_NAME}:latest
                            sudo docker run -d --name fastapi_app -p 80:80 \
                            -e DATABASE_URL=${DATABASE_URL} \
                            -e SECRET_KEY=${SECRET_KEY} \
                            -e ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES} \
                            -e REFRESH_TOKEN_EXPIRE_DAYS=${REFRESH_TOKEN_EXPIRE_DAYS} \
                            -e GROQ_API_KEY=${GROQ_API_KEY} \
                            -e AWS_ACCESS_KEY=${AWS_ACCESS_KEY} \
                            -e AWS_SECRET_KEY=${AWS_SECRET_KEY} \
                            ${env.IMAGE_NAME}:latest
                            EOF
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
