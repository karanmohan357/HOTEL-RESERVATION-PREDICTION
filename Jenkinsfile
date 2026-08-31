pipeline {
    agent any
    environment {
        VENV_DIR = 'venv'
        AWS_ACCOUNT_ID = '985369018380'
        AWS_REGION = 'ap-south-1'
        ECR_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/ml-project-1"
    }
    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/data-guru0/MLOPS-COURSE-PROJECT-1.git']])
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
                        mkdir -p ~/.aws
                        cp $AWS_CRED_FILE ~/.aws/credentials
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                        docker build -t ${ECR_REPO}:latest .
                        docker push ${ECR_REPO}:latest
                        '''
                    }
                }
            }
        }
        stage('Deploy to AWS App Runner') {
            steps {
                withCredentials([file(credentialsId: 'aws-creds-file', variable: 'AWS_CRED_FILE')]) {
                    script {
                        echo 'Deploy to AWS App Runner.............'
                        sh '''
                        mkdir -p ~/.aws
                        cp $AWS_CRED_FILE ~/.aws/credentials
                        aws apprunner update-service \
                            --service-arn $(aws apprunner list-services --region ${AWS_REGION} --query "ServiceSummaryList[?ServiceName=='ml-project'].ServiceArn" --output text) \
                            --source-configuration '{"ImageRepository":{"ImageIdentifier":"'"${ECR_REPO}"':latest","ImageRepositoryType":"ECR"}}' \
                            --region ${AWS_REGION}
                        '''
                    }
                }
            }
        }
    }
}