import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';

export interface CodeReviewQuestStackProps extends cdk.StackProps {
  environment: string;
  config: {
    instanceClass: string;
    minCapacity: number;
    maxCapacity: number;
    desiredCount: number;
    enableDeletionProtection: boolean;
    enableBackup: boolean;
    domainName?: string;
  };
}

export class CodeReviewQuestStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: CodeReviewQuestStackProps) {
    super(scope, id, props);

    const { environment, config } = props;

    // ===========================================
    // VPC - Cost Optimized (2 AZs only)
    // ===========================================
    const vpc = new ec2.Vpc(this, 'VPC', {
      maxAzs: 2, // Reduce to 2 AZs to minimize NAT Gateway costs
      natGateways: environment === 'prod' ? 2 : 1, // Single NAT Gateway for dev/staging
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 28,
          name: 'Database',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      ],
      enableDnsHostnames: true,
      enableDnsSupport: true,
    });

    // ===========================================
    // Security Groups
    // ===========================================
    const albSecurityGroup = new ec2.SecurityGroup(this, 'ALBSecurityGroup', {
      vpc,
      description: 'Security group for Application Load Balancer',
      allowAllOutbound: true,
    });
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), 'HTTP');
    albSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'HTTPS');

    const ecsSecurityGroup = new ec2.SecurityGroup(this, 'ECSSecurityGroup', {
      vpc,
      description: 'Security group for ECS tasks',
      allowAllOutbound: true,
    });
    ecsSecurityGroup.addIngressRule(albSecurityGroup, ec2.Port.tcp(8000), 'ALB to ECS');

    const databaseSecurityGroup = new ec2.SecurityGroup(this, 'DatabaseSecurityGroup', {
      vpc,
      description: 'Security group for RDS database',
      allowAllOutbound: false,
    });
    databaseSecurityGroup.addIngressRule(ecsSecurityGroup, ec2.Port.tcp(5432), 'ECS to RDS');

    const redisSecurityGroup = new ec2.SecurityGroup(this, 'RedisSecurityGroup', {
      vpc,
      description: 'Security group for Redis',
      allowAllOutbound: false,
    });
    redisSecurityGroup.addIngressRule(ecsSecurityGroup, ec2.Port.tcp(6379), 'ECS to Redis');

    // ===========================================
    // Database Secrets
    // ===========================================
    const databaseSecret = new secretsmanager.Secret(this, 'DatabaseSecret', {
      description: 'Database credentials for Code Review Quest',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'crq_user' }),
        generateStringKey: 'password',
        excludeCharacters: '"@/\\\'',
        passwordLength: 32,
      },
    });

    // ===========================================
    // RDS Aurora Serverless v2 (Cost Optimized)
    // ===========================================
    const dbSubnetGroup = new rds.SubnetGroup(this, 'DatabaseSubnetGroup', {
      vpc,
      description: 'Subnet group for RDS database',
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
    });

    const database = new rds.DatabaseCluster(this, 'Database', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_4,
      }),
      credentials: rds.Credentials.fromSecret(databaseSecret),
      defaultDatabaseName: 'code_review_quest',
      serverlessV2MinCapacity: config.minCapacity,
      serverlessV2MaxCapacity: config.maxCapacity,
      writer: rds.ClusterInstance.serverlessV2('writer'),
      readers: environment === 'prod' ? [
        rds.ClusterInstance.serverlessV2('reader', { scaleWithWriter: true }),
      ] : [],
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      securityGroups: [databaseSecurityGroup],
      subnetGroup: dbSubnetGroup,
      deletionProtection: config.enableDeletionProtection,
      backup: config.enableBackup ? {
        retention: cdk.Duration.days(7),
        preferredWindow: '03:00-04:00',
      } : undefined,
      preferredMaintenanceWindow: 'sun:04:00-sun:05:00',
      cloudwatchLogsExports: ['postgresql'],
      monitoring: {
        interval: cdk.Duration.minutes(1),
      },
    });

    // ===========================================
    // ElastiCache Redis Serverless (Cost Optimized)
    // ===========================================
    const redisSubnetGroup = new elasticache.CfnSubnetGroup(this, 'RedisSubnetGroup', {
      description: 'Subnet group for Redis',
      subnetIds: vpc.privateSubnets.map(subnet => subnet.subnetId),
    });

    const redis = new elasticache.CfnServerlessCache(this, 'Redis', {
      engine: 'redis',
      serverlessCacheConfiguration: {
        maxDataStorage: 1, // 1 GB max storage
        maxEcpuPerSecond: 1000, // 1000 ECPU per second
      },
      description: 'Redis cache for Code Review Quest',
      subnetIds: vpc.privateSubnets.map(subnet => subnet.subnetId),
      securityGroupIds: [redisSecurityGroup.securityGroupId],
    });

    // ===========================================
    // ECS Cluster with Fargate Spot (Cost Optimized)
    // ===========================================
    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
      containerInsights: environment === 'prod', // Only enable for production
    });

    // Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDefinition', {
      memoryLimitMiB: 512, // Minimal memory for cost optimization
      cpu: 256, // Minimal CPU for cost optimization
    });

    // CloudWatch Log Group
    const logGroup = new logs.LogGroup(this, 'LogGroup', {
      logGroupName: `/ecs/code-review-quest-${environment}`,
      retention: environment === 'prod' ? logs.RetentionDays.ONE_MONTH : logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Container Definition
    const container = taskDefinition.addContainer('backend', {
      image: ecs.ContainerImage.fromRegistry('code-review-quest-backend:latest'),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'backend',
        logGroup,
      }),
      environment: {
        ENVIRONMENT: environment,
        LOG_LEVEL: environment === 'prod' ? 'INFO' : 'DEBUG',
        REDIS_URL: `redis://${redis.attrRedisEndpointAddress}:${redis.attrRedisEndpointPort}`,
      },
      secrets: {
        DATABASE_URL: ecs.Secret.fromSecretsManager(databaseSecret, 'engine'),
      },
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
        startPeriod: cdk.Duration.seconds(60),
      },
    });

    container.addPortMappings({
      containerPort: 8000,
      protocol: ecs.Protocol.TCP,
    });

    // ===========================================
    // Application Load Balancer
    // ===========================================
    const alb = new elbv2.ApplicationLoadBalancer(this, 'ALB', {
      vpc,
      internetFacing: true,
      securityGroup: albSecurityGroup,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC,
      },
    });

    const targetGroup = new elbv2.ApplicationTargetGroup(this, 'TargetGroup', {
      vpc,
      port: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        enabled: true,
        path: '/health',
        healthyHttpCodes: '200',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 3,
      },
    });

    const listener = alb.addListener('Listener', {
      port: 80,
      defaultTargetGroups: [targetGroup],
    });

    // ===========================================
    // ECS Service with Fargate Spot
    // ===========================================
    const service = new ecs.FargateService(this, 'Service', {
      cluster,
      taskDefinition,
      desiredCount: config.desiredCount,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [ecsSecurityGroup],
      capacityProviderStrategies: [
        {
          capacityProvider: 'FARGATE_SPOT', // Use Spot instances for cost savings
          weight: environment === 'prod' ? 70 : 100, // 70% Spot for prod, 100% for dev
        },
        ...(environment === 'prod' ? [{
          capacityProvider: 'FARGATE',
          weight: 30, // 30% On-Demand for prod reliability
        }] : []),
      ],
      enableExecuteCommand: environment !== 'prod', // Only for dev/staging
    });

    service.attachToApplicationTargetGroup(targetGroup);

    // Auto Scaling (only for production)
    if (environment === 'prod') {
      const scaling = service.autoScaleTaskCount({
        minCapacity: config.desiredCount,
        maxCapacity: config.maxCapacity,
      });

      scaling.scaleOnCpuUtilization('CpuScaling', {
        targetUtilizationPercent: 70,
        scaleInCooldown: cdk.Duration.minutes(5),
        scaleOutCooldown: cdk.Duration.minutes(2),
      });

      scaling.scaleOnMemoryUtilization('MemoryScaling', {
        targetUtilizationPercent: 80,
        scaleInCooldown: cdk.Duration.minutes(5),
        scaleOutCooldown: cdk.Duration.minutes(2),
      });
    }

    // ===========================================
    // S3 Bucket for Frontend (Cost Optimized)
    // ===========================================
    const frontendBucket = new s3.Bucket(this, 'FrontendBucket', {
      bucketName: `code-review-quest-frontend-${environment}-${this.account}`,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'error.html',
      publicReadAccess: false, // Use CloudFront for access
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: environment === 'prod' ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: environment !== 'prod',
      lifecycleRules: [
        {
          id: 'DeleteIncompleteMultipartUploads',
          abortIncompleteMultipartUploadAfter: cdk.Duration.days(1),
        },
      ],
      intelligentTieringConfigurations: environment === 'prod' ? [
        {
          id: 'IntelligentTiering',
          status: s3.IntelligentTieringStatus.ENABLED,
        },
      ] : [],
    });

    // ===========================================
    // CloudFront Distribution (Cost Optimized)
    // ===========================================
    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OAI', {
      comment: `OAI for Code Review Quest ${environment}`,
    });

    frontendBucket.grantRead(originAccessIdentity);

    const distribution = new cloudfront.Distribution(this, 'Distribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(frontendBucket, {
          originAccessIdentity,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        compress: true,
      },
      additionalBehaviors: {
        '/api/*': {
          origin: new origins.LoadBalancerV2Origin(alb, {
            protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY,
          }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        },
      },
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.minutes(5),
        },
      ],
      priceClass: environment === 'prod' 
        ? cloudfront.PriceClass.PRICE_CLASS_ALL 
        : cloudfront.PriceClass.PRICE_CLASS_100, // Use cheaper price class for dev
      enabled: true,
      comment: `Code Review Quest ${environment}`,
    });

    // ===========================================
    // Outputs
    // ===========================================
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: alb.loadBalancerDnsName,
      description: 'Application Load Balancer DNS name',
    });

    new cdk.CfnOutput(this, 'CloudFrontURL', {
      value: `https://${distribution.distributionDomainName}`,
      description: 'CloudFront distribution URL',
    });

    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: database.clusterEndpoint.hostname,
      description: 'RDS cluster endpoint',
    });

    new cdk.CfnOutput(this, 'RedisEndpoint', {
      value: redis.attrRedisEndpointAddress,
      description: 'Redis endpoint',
    });

    new cdk.CfnOutput(this, 'FrontendBucketName', {
      value: frontendBucket.bucketName,
      description: 'S3 bucket name for frontend',
    });

    // Cost optimization tags
    cdk.Tags.of(this).add('CostOptimization', 'Enabled');
    cdk.Tags.of(this).add('AutoShutdown', environment !== 'prod' ? 'Enabled' : 'Disabled');
  }
}
