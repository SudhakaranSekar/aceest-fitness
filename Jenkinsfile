pipeline {
    agent any

    environment {
        PYTHON = 'C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/SudhakaranSekar/aceest-fitness.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                bat '"%PYTHON%" -m pip install flake8 && "%PYTHON%" -m flake8 app.py --select=E9,F63,F7,F82 --show-source'
            }
        }

        stage('Unit Tests') {
            steps {
                bat '"%PYTHON%" -m pytest tests/test_app.py -v'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t aceest-fitness:latest .'
            }
        }
    }

    post {
        success { echo 'BUILD PASSED - all stages completed successfully.' }
        failure { echo 'BUILD FAILED - check stage logs above.' }
    }
}
