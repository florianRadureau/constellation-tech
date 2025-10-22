"""
Dictionnaire exhaustif des technologies avec catégorisation.

Ce dictionnaire sert de référentiel pour:
- Détecter les technologies dans les CV
- Catégoriser automatiquement les compétences
- Associer les couleurs pour la visualisation
"""

TECH_CATEGORIES = {
    "Frontend": {
        "keywords": [
            # Frameworks/Libraries
            "angular", "react", "vue", "vuejs", "svelte", "nextjs", "next.js",
            "nuxt", "nuxtjs", "ember", "backbone", "jquery",
            # Languages
            "typescript", "javascript", "js", "ts", "html", "html5", "css", "css3",
            # Styling
            "sass", "scss", "less", "tailwind", "tailwindcss", "bootstrap",
            "material-ui", "mui", "chakra", "styled-components",
            # Build Tools
            "webpack", "vite", "parcel", "rollup", "esbuild",
            # State Management
            "rxjs", "ngrx", "redux", "mobx", "vuex", "pinia", "zustand",
            # Other
            "webcomponents", "web components", "lit", "stencil"
        ],
        "color": "#DD0031"  # Rouge Angular
    },

    "Backend": {
        "keywords": [
            # Python
            "fastapi", "django", "flask", "tornado", "pyramid", "bottle",
            "aiohttp", "sanic", "quart",
            # JavaScript/TypeScript
            "nodejs", "node.js", "express", "expressjs", "nestjs", "koa",
            "hapi", "fastify", "adonis", "adonisjs",
            # Java
            "spring", "spring boot", "springboot", "java", "hibernate",
            "quarkus", "micronaut",
            # .NET
            "c#", "csharp", ".net", "dotnet", "asp.net", "aspnet",
            # PHP
            "php", "laravel", "symfony", "codeigniter", "yii", "cakephp",
            # Ruby
            "ruby", "rails", "ruby on rails", "sinatra",
            # Go
            "go", "golang", "gin", "echo", "fiber",
            # Rust
            "rust", "actix", "rocket", "axum",
            # Other
            "graphql", "rest", "rest api", "grpc", "websocket"
        ],
        "color": "#009688"  # Teal
    },

    "Database": {
        "keywords": [
            # SQL
            "postgresql", "postgres", "mysql", "mariadb", "sqlite",
            "sql server", "mssql", "oracle", "db2",
            # NoSQL Document
            "mongodb", "mongo", "couchdb", "couchbase",
            # NoSQL Key-Value
            "redis", "memcached", "dynamodb",
            # NoSQL Column
            "cassandra", "hbase", "scylla",
            # NoSQL Graph
            "neo4j", "arangodb", "dgraph",
            # Search
            "elasticsearch", "opensearch", "solr",
            # Time Series
            "influxdb", "timescaledb", "prometheus",
            # Other
            "firebase", "firestore", "supabase"
        ],
        "color": "#4479A1"  # Bleu SQL
    },

    "DevOps": {
        "keywords": [
            # Containers
            "docker", "podman", "containerd",
            # Orchestration
            "kubernetes", "k8s", "openshift", "nomad", "docker swarm",
            "rancher", "helm", "kustomize",
            # CI/CD
            "jenkins", "gitlab ci", "github actions", "circleci", "travis",
            "bamboo", "teamcity", "azure devops", "argocd", "flux",
            # IaC
            "terraform", "terragrunt", "pulumi", "cloudformation",
            "ansible", "puppet", "chef", "salt", "saltstack",
            # Cloud Providers
            "aws", "azure", "gcp", "google cloud", "digitalocean",
            "heroku", "vercel", "netlify", "cloudflare",
            # Monitoring
            "grafana", "prometheus", "datadog", "new relic", "dynatrace",
            "elk", "elasticsearch", "logstash", "kibana", "splunk",
            # Web Servers
            "nginx", "apache", "traefik", "haproxy", "envoy",
            # OS
            "linux", "ubuntu", "debian", "centos", "rhel", "alpine",
            # Other
            "git", "github", "gitlab", "bitbucket", "ci/cd"
        ],
        "color": "#326CE5"  # Bleu Kubernetes
    },

    "AI_ML": {
        "keywords": [
            # Frameworks
            "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
            "jax", "mxnet", "caffe", "theano",
            # LLM/GenAI
            "openai", "gpt", "llm", "gemini", "claude", "mistral",
            "langchain", "llamaindex", "huggingface", "transformers",
            # NLP
            "nlp", "natural language processing", "spacy", "nltk",
            "bert", "gpt-3", "gpt-4",
            # Computer Vision
            "opencv", "computer vision", "yolo", "detectron",
            # Data Science
            "pandas", "numpy", "scipy", "matplotlib", "seaborn",
            "plotly", "jupyter", "notebook",
            # ML Ops
            "mlflow", "kubeflow", "airflow", "prefect",
            # Cloud AI
            "vertex ai", "sagemaker", "azure ml", "databricks",
            # Other
            "deep learning", "machine learning", "reinforcement learning",
            "neural network", "gan"
        ],
        "color": "#FF6F00"  # Orange
    },

    "Mobile": {
        "keywords": [
            # Cross-platform
            "flutter", "react native", "ionic", "cordova", "capacitor",
            "xamarin", "nativescript",
            # Native iOS
            "swift", "swiftui", "objective-c", "ios", "xcode",
            # Native Android
            "kotlin", "android", "java", "jetpack compose",
            # Other
            "dart", "mobile", "app development"
        ],
        "color": "#02569B"  # Bleu Flutter
    },

    "Testing": {
        "keywords": [
            # JavaScript/TypeScript
            "jest", "jasmine", "mocha", "chai", "karma", "ava",
            # E2E
            "cypress", "playwright", "selenium", "puppeteer", "testcafe",
            # Python
            "pytest", "unittest", "nose", "behave",
            # Java
            "junit", "testng", "mockito",
            # Other
            "testing", "test automation", "tdd", "bdd",
            # Quality
            "sonarqube", "sonar", "eslint", "prettier", "black"
        ],
        "color": "#99425B"  # Rouge testing
    },

    "Cloud": {
        "keywords": [
            # AWS Services
            "s3", "ec2", "lambda", "rds", "dynamodb", "cloudfront",
            "route53", "elb", "ecs", "eks", "fargate",
            # GCP Services
            "cloud run", "cloud functions", "bigquery", "cloud storage",
            "app engine", "compute engine", "gke",
            # Azure Services
            "azure functions", "cosmos db", "blob storage", "aks",
            # General
            "serverless", "cloud computing", "iaas", "paas", "saas"
        ],
        "color": "#FF9900"  # Orange AWS
    },

    "Other": {
        "keywords": [
            # Version Control
            "git", "svn", "mercurial",
            # Project Management
            "scrum", "agile", "kanban", "jira", "confluence",
            "trello", "asana", "notion",
            # Architecture
            "microservices", "monolith", "event-driven", "cqrs",
            "domain-driven design", "ddd", "clean architecture",
            # Protocols
            "http", "https", "tcp", "udp", "mqtt", "amqp",
            # Security
            "oauth", "jwt", "ssl", "tls", "authentication", "authorization",
            # Other
            "api", "sdk", "cli"
        ],
        "color": "#808080"  # Gris
    }
}


def get_all_keywords() -> list[str]:
    """
    Retourne la liste plate de tous les mots-clés.

    Returns:
        Liste de tous les mots-clés des technologies
    """
    all_keywords = []
    for category in TECH_CATEGORIES.values():
        all_keywords.extend(category["keywords"])
    return all_keywords


def get_category_for_tech(tech_name: str) -> str:
    """
    Trouve la catégorie d'une technologie.

    Args:
        tech_name: Nom de la technologie (case-insensitive)

    Returns:
        Nom de la catégorie ou "Other" si non trouvée
    """
    tech_lower = tech_name.lower()
    for category, data in TECH_CATEGORIES.items():
        if tech_lower in data["keywords"]:
            return category
    return "Other"


def get_color_for_category(category: str) -> str:
    """
    Retourne la couleur associée à une catégorie.

    Args:
        category: Nom de la catégorie

    Returns:
        Code couleur hexadécimal
    """
    return TECH_CATEGORIES.get(category, TECH_CATEGORIES["Other"])["color"]


def get_color_for_tech(tech_name: str) -> str:
    """
    Retourne la couleur pour une technologie spécifique.

    Args:
        tech_name: Nom de la technologie

    Returns:
        Code couleur hexadécimal
    """
    category = get_category_for_tech(tech_name)
    return get_color_for_category(category)


# Statistiques du dictionnaire
if __name__ == "__main__":
    print("📊 Statistiques du Dictionnaire des Technologies\n")

    total_keywords = 0
    for category, data in TECH_CATEGORIES.items():
        count = len(data["keywords"])
        total_keywords += count
        print(f"  {category:12} : {count:3} technologies ({data['color']})")

    print(f"\n  {'TOTAL':12} : {total_keywords:3} technologies")

    # Tests
    print("\n🔍 Tests de Fonctions:\n")
    test_techs = ["Angular", "FASTAPI", "postgresql", "docker", "unknown"]

    for tech in test_techs:
        category = get_category_for_tech(tech)
        color = get_color_for_tech(tech)
        print(f"  {tech:12} → {category:12} → {color}")