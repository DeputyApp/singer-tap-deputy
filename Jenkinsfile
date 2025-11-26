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
                // Activate the virtual environment and install project and dev dependencies
                sh "source ${VENV}/bin/activate && pip install -e ."
            }
        }

        stage('Linting') {
            steps {
                // Run flake8 to check for code style issues
                sh "source ${VENV}/bin/activate && flake8 tap_deputy/ tests/"
            }
        }

        stage('Run Unit Tests') {
            steps {
                // Activate the virtual environment and execute the test suite
                // The --junitxml flag generates a report for Jenkins
                sh "source ${VENV}/bin/activate && pytest --junitxml=junit.xml"
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
