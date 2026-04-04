pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/SudhakaranSekar/aceest-fitness.git'
            }
        }

        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'python -m py_compile app.py'
            }
        }

        stage('Test') {
            steps {
                sh 'python -m pytest tests/test_app.py -v'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t aceest-fitness .'
            }
        }
    }

    post {
        success {
            echo 'Build and tests passed successfully!'
        }
        failure {
            echo 'Build or tests failed.'
        }
    }
}
