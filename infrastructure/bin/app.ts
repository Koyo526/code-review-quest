#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CodeReviewQuestStack } from '../lib/code-review-quest-stack';
import { CodeReviewQuestPipelineStack } from '../lib/pipeline-stack';

const app = new cdk.App();

// Get environment configuration
const account = process.env.CDK_DEFAULT_ACCOUNT;
const region = process.env.CDK_DEFAULT_REGION || 'us-east-1';
const environment = process.env.ENVIRONMENT || 'dev';

// Environment-specific configuration
const envConfig = {
  dev: {
    instanceClass: 't3.micro',
    minCapacity: 0.5,
    maxCapacity: 1,
    desiredCount: 1,
    enableDeletionProtection: false,
    enableBackup: false,
    domainName: undefined, // No custom domain for dev
  },
  staging: {
    instanceClass: 't3.small',
    minCapacity: 0.5,
    maxCapacity: 2,
    desiredCount: 1,
    enableDeletionProtection: false,
    enableBackup: true,
    domainName: undefined,
  },
  prod: {
    instanceClass: 't3.medium',
    minCapacity: 1,
    maxCapacity: 4,
    desiredCount: 2,
    enableDeletionProtection: true,
    enableBackup: true,
    domainName: 'codereviewquest.com', // Custom domain for production
  }
};

const config = envConfig[environment as keyof typeof envConfig] || envConfig.dev;

// Main application stack
new CodeReviewQuestStack(app, `CodeReviewQuest-${environment}`, {
  env: { account, region },
  environment,
  config,
  tags: {
    Project: 'CodeReviewQuest',
    Environment: environment,
    CostCenter: 'Development',
    Owner: 'DevTeam',
  },
});

// CI/CD Pipeline stack (only for production)
if (environment === 'prod') {
  new CodeReviewQuestPipelineStack(app, 'CodeReviewQuest-Pipeline', {
    env: { account, region },
    tags: {
      Project: 'CodeReviewQuest',
      Environment: 'pipeline',
      CostCenter: 'Development',
      Owner: 'DevTeam',
    },
  });
}
