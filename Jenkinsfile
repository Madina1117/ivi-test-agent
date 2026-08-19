pipeline {
    agent any

    parameters {
        booleanParam(name: 'REAL_DEVICE', defaultValue: false,
            description: 'Run against a real head unit / emulator instead of the mock driver')
        string(name: 'UDID', defaultValue: '', description: 'Device UDID (only used when REAL_DEVICE is true)')
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '. .venv/bin/activate && ruff check .'
            }
        }

        stage('Test') {
            steps {
                script {
                    def deviceFlag = params.REAL_DEVICE ? "--real-device --udid ${params.UDID}" : ''
                    sh """
                        . .venv/bin/activate
                        python -m pytest ${deviceFlag} \
                            --html=results/report.html --self-contained-html \
                            --junitxml=results/junit.xml -v
                    """
                }
            }
        }
    }

    post {
        always {
            junit 'results/junit.xml'
            archiveArtifacts artifacts: 'results/**', allowEmptyArchive: true
        }
    }
}
