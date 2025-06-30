.PHONY: help dev build test lint clean seed-db logs stop aws-deploy-dev aws-deploy-staging aws-deploy-prod aws-build-backend aws-build-frontend aws-cost-estimate

# Default target
help: ## Show this help message
	@echo "Code Review Quest - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose up -d

build: ## Build all containers
	@echo "🐳 Building containers..."
	docker-compose build

test: ## Run tests
	@echo "🧪 Running tests..."
	docker-compose exec backend python -m pytest

lint: ## Run linting
	@echo "🔍 Running linting..."
	docker-compose exec backend python -m pylint app/

clean: ## Clean up containers and volumes
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f

logs: ## Show logs
	@echo "📋 Showing logs..."
	docker-compose logs -f

stop: ## Stop all services
	@echo "🛑 Stopping services..."
	docker-compose down

# Database
init-db: ## Initialize database with sample data
	@echo "🗄️ Initializing database..."
	python scripts/init_database.py

migrate: ## Run database migrations
	@echo "🔄 Running database migrations..."
	docker-compose exec backend alembic upgrade head

migrate-create: ## Create a new migration
	@echo "📝 Creating new migration..."
	@read -p "Enter migration message: " msg; \
	docker-compose exec backend alembic revision --autogenerate -m "$$msg"

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose exec backend alembic downgrade base; \
		docker-compose exec backend alembic upgrade head; \
		python scripts/init_database.py; \
		echo "✅ Database reset completed"; \
	else \
		echo "❌ Database reset cancelled"; \
	fi

seed-db: ## Initialize database with sample data
	@echo "🌱 Seeding database with sample data..."
	python scripts/init_database.py

# AWS Deployment
aws-deploy-dev: ## Deploy to AWS development environment
	@echo "🚀 Deploying to AWS development environment..."
	./scripts/deploy.sh dev

aws-deploy-staging: ## Deploy to AWS staging environment
	@echo "🚀 Deploying to AWS staging environment..."
	./scripts/deploy.sh staging

aws-deploy-prod: ## Deploy to AWS production environment
	@echo "🚀 Deploying to AWS production environment..."
	./scripts/deploy.sh prod

aws-build-backend: ## Build backend Docker image for AWS
	@echo "🐳 Building backend Docker image for AWS..."
	cd backend && docker build -f Dockerfile.aws -t code-review-quest-backend:latest .

aws-build-frontend: ## Build frontend for AWS deployment
	@echo "🏗️ Building frontend for AWS deployment..."
	cd frontend && npm run build

aws-push-images: ## Push Docker images to ECR
	@echo "📤 Pushing Docker images to ECR..."
	@echo "Please run the ECR login command first:"
	@echo "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com"

aws-logs: ## View ECS logs
	@echo "📋 Viewing ECS logs..."
	aws logs tail /ecs/code-review-quest-dev --follow

aws-status: ## Check AWS deployment status
	@echo "📊 Checking AWS deployment status..."
	aws cloudformation describe-stacks --stack-name CodeReviewQuest-dev --query 'Stacks[0].StackStatus'

aws-destroy-dev: ## Destroy AWS development environment
	@echo "⚠️ Destroying AWS development environment..."
	@read -p "Are you sure? This will delete all resources! (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		cd infrastructure && cdk destroy CodeReviewQuest-dev --force; \
	else \
		echo "❌ Destruction cancelled"; \
	fi

aws-cost-estimate: ## Show estimated AWS costs
	@echo "💰 AWS Cost Estimation:"
	@echo "======================="
	@echo "Development: ~$40-70/month"
	@echo "Staging: ~$55-100/month"
	@echo "Production: ~$95-220/month"
	@echo ""
	@echo "💡 Cost breakdown available in deployment script"
	@echo "🚀 Starting Code Review Quest development environment..."
	docker-compose up -d db redis
	@echo "⏳ Waiting for database to be ready..."
	@sleep 10
	docker-compose up --build backend worker frontend

dev-detached: ## Start development environment in background
	docker-compose up -d --build

# Database
# Database
init-db: ## Initialize database with sample data
	@echo "🗄️ Initializing database..."
	python scripts/init_database.py

migrate: ## Run database migrations
	@echo "🔄 Running database migrations..."
	docker-compose exec backend alembic upgrade head

migrate-create: ## Create a new migration
	@echo "📝 Creating new migration..."
	@read -p "Enter migration message: " msg; \
	docker-compose exec backend alembic revision --autogenerate -m "$$msg"

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose exec backend alembic downgrade base; \
		docker-compose exec backend alembic upgrade head; \
		python scripts/init_database.py; \
		echo "✅ Database reset completed"; \
	else \
		echo "❌ Database reset cancelled"; \
	fi

seed-db: ## Initialize database with sample data
	@echo "🌱 Seeding database with sample data..."
	python scripts/init_database.py

migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

# Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend: ## Run backend tests
	@echo "🐍 Running backend tests..."
	docker-compose exec backend pytest app/tests/ -v --cov=app

test-frontend: ## Run frontend tests
	@echo "⚛️  Running frontend tests..."
	docker-compose exec frontend npm test

test-worker: ## Run worker tests
	@echo "🔧 Running worker tests..."
	docker-compose exec worker pytest tests/ -v

# Linting
lint: ## Run linting for all components
	$(MAKE) lint-backend
	$(MAKE) lint-frontend
	$(MAKE) lint-worker

lint-backend: ## Run backend linting
	@echo "🐍 Linting backend code..."
	docker-compose exec backend black app/ --check
	docker-compose exec backend isort app/ --check-only
	docker-compose exec backend flake8 app/
	docker-compose exec backend mypy app/

lint-frontend: ## Run frontend linting
	@echo "⚛️  Linting frontend code..."
	docker-compose exec frontend npm run lint
	docker-compose exec frontend npm run type-check

lint-worker: ## Run worker linting
	@echo "🔧 Linting worker code..."
	docker-compose exec worker black . --check
	docker-compose exec worker isort . --check-only
	docker-compose exec worker flake8 .

# Formatting
format: ## Format all code
	$(MAKE) format-backend
	$(MAKE) format-frontend
	$(MAKE) format-worker

format-backend: ## Format backend code
	docker-compose exec backend black app/
	docker-compose exec backend isort app/

format-frontend: ## Format frontend code
	docker-compose exec frontend npm run format

format-worker: ## Format worker code
	docker-compose exec worker black .
	docker-compose exec worker isort .

# Building
build: ## Build all services
	@echo "🏗️  Building all services..."
	docker-compose build

build-backend: ## Build backend service
	docker-compose build backend

build-frontend: ## Build frontend service
	docker-compose build frontend

build-worker: ## Build worker service
	docker-compose build worker

# Production build
build-prod: ## Build for production
	@echo "🏭 Building for production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Logs
logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-worker: ## Show worker logs
	docker-compose logs -f worker

logs-db: ## Show database logs
	docker-compose logs -f db

# Management
stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	docker-compose down

clean: ## Clean up containers, volumes, and images
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f

restart: ## Restart all services
	$(MAKE) stop
	$(MAKE) dev

# Database management
db-shell: ## Connect to database shell
	docker-compose exec db psql -U crq_user -d code_review_quest

db-backup: ## Backup database
	@echo "💾 Creating database backup..."
	docker-compose exec db pg_dump -U crq_user code_review_quest > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Development utilities
shell-backend: ## Open backend container shell
	docker-compose exec backend bash

shell-frontend: ## Open frontend container shell
	docker-compose exec frontend sh

shell-worker: ## Open worker container shell
	docker-compose exec worker bash

# Install dependencies
install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	cd frontend && npm install
	cd backend && pip install -r requirements.txt
	cd worker && pip install -r requirements.txt

# Security
security-check: ## Run security checks
	@echo "🔒 Running security checks..."
	docker-compose exec backend safety check
	docker-compose exec frontend npm audit
	docker-compose exec worker safety check

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	docker-compose exec backend python -m mkdocs serve

# Health check
health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend unhealthy"
	@curl -f http://localhost:3000 || echo "❌ Frontend unhealthy"
	@docker-compose exec redis redis-cli ping || echo "❌ Redis unhealthy"
	@docker-compose exec db pg_isready -U crq_user -d code_review_quest || echo "❌ Database unhealthy"
