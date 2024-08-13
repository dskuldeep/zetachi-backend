pipeline {
    agent any

    environment {
        // Jenkins credentials for environment variables
        DATABASE_URL = credentials('DATABASE_URL')
        SECRET_KEY = credentials('SECRET_KEY')
        ACCESS_TOKEN_EXPIRE_MINUTES = credentials('ACCESS_TOKEN_EXPIRE_MINUTES')
        REFRESH_TOKEN_EXPIRE_DAYS = credentials('REFRESH_TOKEN_EXPIRE_DAYS')
        GROQ_API_KEY = credentials('GROQ_API_KEY')
        AWS_ACCESS_KEY = credentials('AWS_ACCESS_KEY')
        AWS_SECRET_KEY = credentials('AWS_SECRET_KEY')

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
                    withEnv(["DOCKER_HOST=${env.DOCKER_HOST}"]) {
                        dockerImage = docker.build("${env.IMAGE_NAME}")
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    withEnv(["DOCKER_HOST=${env.DOCKER_HOST}"]) {
                        docker.withRegistry('https://index.docker.io/v1/', env.DOCKERHUB_CREDENTIALS) {
                            dockerImage.push("${env.BUILD_NUMBER}")
                            dockerImage.push('latest')
                        }
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                script {
                    sshagent([env.SSH_CREDENTIALS]) {
                        withEnv([
                            "DATABASE_URL=${env.DATABASE_URL}",
                            "SECRET_KEY=${env.SECRET_KEY}",
                            "ACCESS_TOKEN_EXPIRE_MINUTES=${env.ACCESS_TOKEN_EXPIRE_MINUTES}",
                            "REFRESH_TOKEN_EXPIRE_DAYS=${env.REFRESH_TOKEN_EXPIRE_DAYS}",
                            "GROQ_API_KEY=${env.GROQ_API_KEY}",
                            "AWS_ACCESS_KEY=${env.AWS_ACCESS_KEY}",
                            "AWS_SECRET_KEY=${env.AWS_SECRET_KEY}"
                        ]) {
                            sh """
                            ssh -o StrictHostKeyChecking=no ubuntu@${env.AWS_EC2_IP} << 'EOF'
                            docker pull ${env.IMAGE_NAME}:latest
                            docker stop fastapi_app || true
                            docker rm fastapi_app || true
                            docker run -d --name fastapi_app -p 80:80 \
                            -e DATABASE_URL=\${DATABASE_URL} \
                            -e SECRET_KEY=\${SECRET_KEY} \
                            -e ACCESS_TOKEN_EXPIRE_MINUTES=\${ACCESS_TOKEN_EXPIRE_MINUTES} \
                            -e REFRESH_TOKEN_EXPIRE_DAYS=\${REFRESH_TOKEN_EXPIRE_DAYS} \
                            -e GROQ_API_KEY=\${GROQ_API_KEY} \
                            -e AWS_ACCESS_KEY=\${AWS_ACCESS_KEY} \
                            -e AWS_SECRET_KEY=\${AWS_SECRET_KEY} \
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
