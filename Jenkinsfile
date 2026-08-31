pipeline {
    agent any
    environment {
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '985369018380'
        AWS_REGION = 'ap-south-1'
        ECR_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ml-project"
        LAMBDA_FUNCTION_NAME = 'ml-project-1'
    }
    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/karanmohan357/HOTEL-RESERVATION-PREDICTION.git']])
                }
            }
        }
        stage('Setting up our Virtual Environment and Installing dependancies') {
            steps {
                script {
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
        stage('Building and Pushing Docker Image to ECR') {
            steps {
                withCredentials([file(credentialsId: 'aws-creds-file', variable: 'AWS_CRED_FILE')]) {
                    script {
                        echo 'Building and Pushing Docker Image to ECR.............'
                        sh '''
                        export AWS_SHARED_CREDENTIALS_FILE=${AWS_CRED_FILE}

                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                        docker build -t ${ECR_REPO}:latest .
                        docker push ${ECR_REPO}:latest
                        '''
                    }
                }
            }
        }
        stage('Deploy to AWS Lambda') {
            steps {
                withCredentials([file(credentialsId: 'aws-creds-file', variable: 'AWS_CRED_FILE')]) {
                    script {
                        echo 'Deploy to AWS Lambda.............'
                        sh '''
                        export AWS_SHARED_CREDENTIALS_FILE=${AWS_CRED_FILE}

                        aws lambda update-function-code \
                            --function-name ${LAMBDA_FUNCTION_NAME} \
                            --image-uri ${ECR_REPO}:latest \
                            --region ${AWS_REGION}

                        aws lambda wait function-updated \
                            --function-name ${LAMBDA_FUNCTION_NAME} \
                            --region ${AWS_REGION}
                        '''
                    }
                }
            }
        }
    }
}