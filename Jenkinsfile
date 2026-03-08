pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/<your-username>/aceest-fitness.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'flake8 app.py --select=E9,F63,F7,F82 --show-source'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'pytest tests/test_app.py -v --tb=short'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t aceest-fitness:jenkins-${BUILD_NUMBER} .'
            }
        }
    }

    post {
        success { echo 'BUILD PASSED — all stages completed successfully.' }
        failure { echo 'BUILD FAILED — check stage logs above.' }
        always  { sh 'docker rmi aceest-fitness:jenkins-${BUILD_NUMBER} || true' }
    }
}
