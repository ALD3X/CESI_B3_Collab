// Pipeline CI/CD de la boutique — Jenkins (job multi-branches)
// Mêmes étapes et mêmes commandes que les workflows de .github/workflows/ : les scripts du package.json
// (npm run …). Les contrôles qui tournent dans l'image de leur outil (gitleaks, Semgrep, Trivy) appellent
// directement le script commun infra/ci/controles-securite.sh, ces images n'ayant pas Node.js.
// Monorepo turbo : toutes les commandes partent de la racine du dépôt (apps/, infra/, tools/).
//
// Branches et environnements :
//   feature/*, dev : intégration continue UNIQUEMENT (contrôles, images, scan, test de bout en bout),
//                    aucune publication, aucun déploiement
//   accp      : images construites UNE fois et publiées (v-<version>), déployées en recette (Kubernetes), recette validée
//   prod      : version recettée uniquement, APPROBATION manuelle, déploiement progressif (Kubernetes),
//               test de fumée, retour arrière automatique
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        COMPOSE_FILE   = 'infra/compose/compose.yaml'   // fichier Docker Compose de la boutique
        TRIVY_IMAGE    = 'aquasec/trivy:0.65.0'
        REGISTRE       = 'localhost:5000/'          // registre local (équivalent de GHCR)
        CHARGER_IMAGES = 'minikube:boutique'        // les images sont chargées dans les nœuds du cluster local
        KUBECONFIG     = '/var/jenkins_home/.kube/config'
    }

    stages {
        stage('Version') {
            steps {
                script {
                    env.VERSION = sh(script: 'npm run -s images:version', returnStdout: true).trim()
                    env.TAG = "v-${env.VERSION}"
                    env.PROJET_CI = "boutique-ci-${env.BRANCH_NAME.replaceAll('[^a-zA-Z0-9]', '').toLowerCase()}-${env.BUILD_NUMBER}"
                    currentBuild.description = "${env.BRANCH_NAME} · ${env.TAG}"
                }
            }
        }

        // ---------- 1. Qualité et sécurité du code (toutes les branches) ----------
        stage('Qualité et sécurité du code') {
            parallel {
                stage('Secrets (gitleaks)') {
                    agent { docker { image 'zricethezav/gitleaks:v8.24.3'; args '--entrypoint='; reuseNode true } }
                    steps { sh 'sh infra/ci/controles-securite.sh secrets' }
                }
                stage('Backend : tests + couverture') {
                    agent { docker { image 'maven:3.9-eclipse-temurin-25'; args '-v boutique-m2:/root/.m2'; reuseNode true } }
                    // Même commande que la tâche turbo « test » de apps/back (ici dans l'image Maven, sans Node)
                    steps { sh 'mvn -B -ntp -f apps/back/pom.xml verify' }
                    post {
                        always { junit allowEmptyResults: true, testResults: 'apps/back/*/target/surefire-reports/*.xml' }
                    }
                }
                stage('Front : tests + couverture') {
                    agent { docker { image 'node:26-alpine'; reuseNode true } }
                    // Espaces de travail npm du monorepo, tâche turbo « test » du front
                    steps { sh 'npm ci && npm run test:front' }
                }
                stage('SAST (Semgrep) + SCA (Trivy)') {
                    stages {
                        stage('SAST') {
                            agent { docker { image 'semgrep/semgrep:1.99.0'; reuseNode true } }
                            steps {
                                sh 'sh infra/ci/controles-securite.sh sast'
                            }
                        }
                        stage('SCA') {
                            agent { docker { image 'aquasec/trivy:0.65.0'; args '--entrypoint='; reuseNode true } }
                            steps {
                                sh 'sh infra/ci/controles-securite.sh sca'
                            }
                        }
                    }
                }
            }
        }

        // ---------- 2. Images : construites une seule fois, puis promues ----------
        stage('Images : build, scan, test de bout en bout') {
            // Sur prod (ou sur accp en cas de relance), les images de la version existent déjà : on les reprend.
            when {
                expression {
                    !(env.BRANCH_NAME in ['accp', 'prod'] &&
                      sh(script: 'npm run -s images:present', returnStatus: true) == 0)
                }
            }
            steps {
                sh 'npm run images:build'
                sh 'npm run images:scan'
                sh 'npm run test:e2e -- "$PROJET_CI"'
                script {
                    if (env.BRANCH_NAME in ['accp', 'prod']) {      // dev : intégration continue, aucune publication
                        sh 'npm run images:publier'
                    }
                }
            }
        }

        // ---------- 3. Déploiement continu : à partir de la recette (dev ne publie ni ne déploie rien) ----------
        stage('Recette (accp)') {
            when { branch 'accp' }
            steps {
                sh 'npm run deployer -- accp'
                sh 'npm run images:etiqueter -- accp'
                sh 'npm run images:etiqueter -- "accp-$VERSION"'
            }
        }

        stage('Production') {
            when { branch 'prod' }
            stages {
                stage('Contrôle : version recettée') {
                    steps { sh 'npm run -s images:present -- "accp-$VERSION"' }
                }
                stage('Approbation') {
                    steps {
                        timeout(time: 30, unit: 'MINUTES') {
                            input message: "Mettre en production la version ${env.VERSION} (recette validée) ?",
                                  ok: 'Mettre en production', submitter: 'admin'
                        }
                    }
                }
                stage('Déploiement prod') {
                    steps {
                        sh 'npm run deployer -- prod'      // retour arrière automatique en cas d'échec
                        sh 'npm run images:etiqueter -- prod'
                        sh 'npm run images:etiqueter -- "prod-$VERSION"'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'apps/back/*/target/site/jacoco/**, apps/front/coverage/**',
                             allowEmptyArchive: true
        }
        success { echo "Pipeline VERT (${env.BRANCH_NAME}, ${env.TAG})." }
        failure { echo 'Pipeline ROUGE : une quality gate a bloqué la livraison.' }
    }
}
