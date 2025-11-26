pipeline {
    agent {
        docker { image 'python:3.11-slim' }
    }

    environment {
        // Define a virtual environment path to be used across stages
        VENV = "venv"
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the source code from the repository
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                // Ensure python is available and create a virtual environment
                sh 'python --version'
                sh "python -m venv ${VENV}"
            }
        }

        stage('Install Dependencies') {
            steps {
                // Install project and dev dependencies using the pip from the virtualenv
                sh "${VENV}/bin/pip install -e ."
            }
        }

        stage('Linting') {
            steps {
                // Run flake8 to check for code style issues
                sh "${VENV}/bin/flake8 tap_deputy/ tests/"
            }
        }

        stage('Run Unit Tests') {
            steps {
                // Execute the test suite using pytest from the virtualenv
                // The --junitxml flag generates a report for Jenkins
                sh "${VENV}/bin/pytest --junitxml=junit.xml"
            }
        }
    }

    post {
        always {
            // Publish the test results, so they are displayed in the Jenkins UI
            junit 'junit.xml'
        }
    }
}
