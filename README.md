# 🎮 Code Review Quest

Interactive code review learning platform that gamifies the process of finding bugs and improving code quality skills.

## 🌟 Features

- **Interactive Code Review**: Find bugs in real code using Monaco Editor
- **Gamified Learning**: Earn points, badges, and compete on leaderboards
- **Multiple Difficulty Levels**: From beginner to advanced challenges
- **Detailed Explanations**: Learn from mistakes with comprehensive feedback
- **Progress Tracking**: Monitor your improvement over time
- **Database Persistence**: All progress saved and tracked

## 🏗️ Architecture

### Local Development
- **Frontend**: React + TypeScript + Vite + Monaco Editor
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Cache**: Redis for session management
- **Containerization**: Docker + Docker Compose

### AWS Production (Cost-Optimized)
- **Compute**: ECS Fargate with Spot instances (up to 70% cost savings)
- **Database**: RDS Aurora Serverless v2 (pay-per-use scaling)
- **Cache**: ElastiCache Serverless (usage-based pricing)
- **Frontend**: S3 + CloudFront (global CDN)
- **Load Balancer**: Application Load Balancer
- **Infrastructure**: AWS CDK (Infrastructure as Code)

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/code-review-quest.git
   cd code-review-quest
   ```

2. **Start the development environment**
   ```bash
   make dev
   ```

3. **Initialize the database**
   ```bash
   make init-db
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### AWS Deployment

#### Prerequisites
- AWS CLI configured with appropriate permissions
- AWS CDK installed (`npm install -g aws-cdk`)
- Docker installed for building images

#### Deploy to Development Environment
```bash
# Deploy infrastructure
make aws-deploy-dev

# Build and push images (after ECR is created)
make aws-build-backend
make aws-build-frontend

# Check deployment status
make aws-status
```

#### Deploy to Production
```bash
# Deploy to production (includes CI/CD pipeline)
make aws-deploy-prod
```

## 💰 Cost Optimization

### Estimated Monthly Costs

| Environment | Estimated Cost | Key Features |
|-------------|----------------|--------------|
| Development | $40-70/month | Spot instances, auto-shutdown, minimal resources |
| Staging | $55-100/month | Mixed instances, backup enabled |
| Production | $95-220/month | High availability, full monitoring, backups |

### Cost-Saving Features
- **Fargate Spot Instances**: Up to 70% savings on compute
- **Aurora Serverless v2**: Pay only for actual database usage
- **ElastiCache Serverless**: Usage-based Redis pricing
- **Auto-Shutdown**: Automatically stops dev/staging environments after hours
- **Intelligent Tiering**: S3 storage optimization
- **CloudFront**: Reduced bandwidth costs with global caching

## 🛠️ Development Commands

```bash
# Local Development
make dev              # Start development environment
make build            # Build all containers
make logs             # View logs
make test             # Run tests
make clean            # Clean up containers

# Database Management
make init-db          # Initialize database with sample data
make migrate          # Run database migrations
make db-reset         # Reset database (WARNING: deletes all data)

# AWS Deployment
make aws-deploy-dev   # Deploy to AWS development
make aws-deploy-prod  # Deploy to AWS production
make aws-cost-estimate # Show cost estimates
make aws-destroy-dev  # Destroy development environment
```

## 📊 Monitoring & Observability

### Local Development
- **Health Checks**: `/health` endpoint for service status
- **Logs**: Structured logging with different levels
- **Database**: PostgreSQL with connection pooling

### AWS Production
- **CloudWatch**: Centralized logging and metrics
- **ECS Health Checks**: Automatic container health monitoring
- **RDS Monitoring**: Database performance insights
- **Cost Alerts**: Budget notifications and alerts
- **Auto-Scaling**: Automatic scaling based on CPU/memory usage

## 🔒 Security

- **Container Security**: Non-root user in containers
- **Database**: Encrypted at rest and in transit
- **Secrets Management**: AWS Secrets Manager for credentials
- **Network Security**: VPC with private subnets
- **HTTPS**: SSL/TLS encryption via CloudFront

## 🎯 Game Mechanics

### Problem Categories
- **Runtime Errors**: Division by zero, null pointer exceptions
- **Logic Errors**: Off-by-one errors, incorrect algorithms
- **Security Issues**: SQL injection, XSS vulnerabilities
- **Resource Management**: Memory leaks, file handle issues
- **Concurrency**: Race conditions, deadlocks

### Scoring System
- **Base Points**: 100 points per problem
- **Correct Bug**: +50 points per bug found
- **False Positive**: -10 points per incorrect report
- **Time Bonus**: Extra points for quick completion
- **Accuracy Bonus**: Bonus for high accuracy rates

### Badge System
- 🐛 **First Bug Hunter**: Find your first bug
- 🎯 **Perfect Score**: Achieve 100% accuracy
- 🏆 **Bug Master**: Find 50+ bugs total
- 🔒 **Security Expert**: Complete 5 security challenges
- ⚡ **Speed Demon**: Complete challenge in under 2 minutes
- 📚 **Persistent Learner**: Complete 10 challenges
- 🔥 **Advanced Challenger**: Complete 3 advanced challenges

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Monaco Editor for the code editing experience
- FastAPI for the robust backend framework
- React ecosystem for the frontend
- AWS for the cloud infrastructure
- All contributors and testers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/code-review-quest/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/code-review-quest/discussions)
- **Email**: support@codereviewquest.com

---

**Happy Bug Hunting! 🐛🎯**
