import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as budgets from 'aws-cdk-lib/aws-budgets';

export interface CostOptimizationProps {
  environment: string;
  monthlyBudgetLimit: number;
  alertEmail: string;
}

export class CostOptimizationConstruct extends Construct {
  constructor(scope: Construct, id: string, props: CostOptimizationProps) {
    super(scope, id);

    const { environment, monthlyBudgetLimit, alertEmail } = props;

    // ===========================================
    // Budget Alerts
    // ===========================================
    new budgets.CfnBudget(this, 'MonthlyBudget', {
      budget: {
        budgetName: `code-review-quest-${environment}-budget`,
        budgetLimit: {
          amount: monthlyBudgetLimit,
          unit: 'USD',
        },
        timeUnit: 'MONTHLY',
        budgetType: 'COST',
        costFilters: {
          TagKey: ['Project'],
          TagValue: ['CodeReviewQuest'],
        },
      },
      notificationsWithSubscribers: [
        {
          notification: {
            notificationType: 'ACTUAL',
            comparisonOperator: 'GREATER_THAN',
            threshold: 80, // Alert at 80% of budget
            thresholdType: 'PERCENTAGE',
          },
          subscribers: [
            {
              subscriptionType: 'EMAIL',
              address: alertEmail,
            },
          ],
        },
        {
          notification: {
            notificationType: 'FORECASTED',
            comparisonOperator: 'GREATER_THAN',
            threshold: 100, // Alert when forecasted to exceed budget
            thresholdType: 'PERCENTAGE',
          },
          subscribers: [
            {
              subscriptionType: 'EMAIL',
              address: alertEmail,
            },
          ],
        },
      ],
    });

    // ===========================================
    // Auto-Shutdown Lambda (for dev/staging)
    // ===========================================
    if (environment !== 'prod') {
      const autoShutdownLambda = new lambda.Function(this, 'AutoShutdownLambda', {
        runtime: lambda.Runtime.PYTHON_3_11,
        handler: 'index.handler',
        code: lambda.Code.fromInline(`
import boto3
import json

def handler(event, context):
    """
    Auto-shutdown function for non-production environments
    Stops ECS services and scales down RDS during off-hours
    """
    
    ecs_client = boto3.client('ecs')
    rds_client = boto3.client('rds')
    
    try:
        # Get cluster name from environment
        cluster_name = f"code-review-quest-{environment}"
        
        # Stop ECS services
        services = ecs_client.list_services(cluster=cluster_name)
        for service_arn in services['serviceArns']:
            ecs_client.update_service(
                cluster=cluster_name,
                service=service_arn,
                desiredCount=0
            )
            print(f"Stopped ECS service: {service_arn}")
        
        # Scale down RDS Aurora Serverless
        clusters = rds_client.describe_db_clusters()
        for cluster in clusters['DBClusters']:
            if cluster['DBClusterIdentifier'].startswith(f"code-review-quest-{environment}"):
                # Aurora Serverless v2 will automatically scale to minimum
                print(f"RDS cluster {cluster['DBClusterIdentifier']} will auto-scale down")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Auto-shutdown completed successfully')
        }
        
    except Exception as e:
        print(f"Error during auto-shutdown: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
        `),
        environment: {
          ENVIRONMENT: environment,
        },
        timeout: cdk.Duration.minutes(5),
      });

      // Grant necessary permissions
      autoShutdownLambda.addToRolePolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'ecs:ListServices',
          'ecs:UpdateService',
          'ecs:DescribeServices',
          'rds:DescribeDBClusters',
          'rds:ModifyDBCluster',
        ],
        resources: ['*'],
      }));

      // Schedule auto-shutdown for evenings (6 PM UTC)
      const shutdownRule = new events.Rule(this, 'ShutdownRule', {
        schedule: events.Schedule.cron({
          minute: '0',
          hour: '18', // 6 PM UTC
          weekDay: 'MON-FRI', // Weekdays only
        }),
        description: `Auto-shutdown for ${environment} environment`,
      });

      shutdownRule.addTarget(new targets.LambdaFunction(autoShutdownLambda));

      // Auto-startup Lambda for mornings
      const autoStartupLambda = new lambda.Function(this, 'AutoStartupLambda', {
        runtime: lambda.Runtime.PYTHON_3_11,
        handler: 'index.handler',
        code: lambda.Code.fromInline(`
import boto3
import json

def handler(event, context):
    """
    Auto-startup function for non-production environments
    Starts ECS services in the morning
    """
    
    ecs_client = boto3.client('ecs')
    
    try:
        # Get cluster name from environment
        cluster_name = f"code-review-quest-{environment}"
        
        # Start ECS services
        services = ecs_client.list_services(cluster=cluster_name)
        for service_arn in services['serviceArns']:
            ecs_client.update_service(
                cluster=cluster_name,
                service=service_arn,
                desiredCount=1  # Start with 1 task
            )
            print(f"Started ECS service: {service_arn}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Auto-startup completed successfully')
        }
        
    except Exception as e:
        print(f"Error during auto-startup: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
        `),
        environment: {
          ENVIRONMENT: environment,
        },
        timeout: cdk.Duration.minutes(5),
      });

      // Grant necessary permissions
      autoStartupLambda.addToRolePolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'ecs:ListServices',
          'ecs:UpdateService',
          'ecs:DescribeServices',
        ],
        resources: ['*'],
      }));

      // Schedule auto-startup for mornings (8 AM UTC)
      const startupRule = new events.Rule(this, 'StartupRule', {
        schedule: events.Schedule.cron({
          minute: '0',
          hour: '8', // 8 AM UTC
          weekDay: 'MON-FRI', // Weekdays only
        }),
        description: `Auto-startup for ${environment} environment`,
      });

      startupRule.addTarget(new targets.LambdaFunction(autoStartupLambda));
    }

    // ===========================================
    // Cost Monitoring Dashboard
    // ===========================================
    // Note: CloudWatch Dashboard creation would go here
    // Omitted for brevity, but would include cost metrics and resource utilization
  }
}
