import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ecr from 'aws-cdk-lib/aws-ecr';

export class CodeReviewQuestPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ===========================================
    // ECR Repository
    // ===========================================
    const ecrRepository = new ecr.Repository(this, 'ECRRepository', {
      repositoryName: 'code-review-quest',
      imageScanOnPush: true,
      lifecycleRules: [
        {
          description: 'Keep last 10 images',
          maxImageCount: 10,
        },
      ],
    });

    // ===========================================
    // S3 Bucket for Pipeline Artifacts
    // ===========================================
    const artifactsBucket = new s3.Bucket(this, 'ArtifactsBucket', {
      bucketName: `code-review-quest-pipeline-artifacts-${this.account}`,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      lifecycleRules: [
        {
          id: 'DeleteOldVersions',
          noncurrentVersionExpiration: cdk.Duration.days(30),
        },
      ],
    });

    // ===========================================
    // CodeBuild Projects
    // ===========================================
    
    // Backend Build Project
    const backendBuildProject = new codebuild.Project(this, 'BackendBuild', {
      projectName: 'code-review-quest-backend-build',
      source: codebuild.Source.codeCommit({
        repository: codebuild.Repository.gitHub({
          owner: 'your-github-username', // Replace with actual GitHub username
          repo: 'code-review-quest',
        }),
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        privileged: true, // Required for Docker builds
        computeType: codebuild.ComputeType.SMALL, // Cost optimization
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          pre_build: {
            commands: [
              'echo Logging in to Amazon ECR...',
              'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
              'REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/code-review-quest',
              'COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)',
              'IMAGE_TAG=${COMMIT_HASH:=latest}',
            ],
          },
          build: {
            commands: [
              'echo Build started on `date`',
              'echo Building the Docker image...',
              'cd backend',
              'docker build -t $REPOSITORY_URI:latest .',
              'docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG',
            ],
          },
          post_build: {
            commands: [
              'echo Build completed on `date`',
              'echo Pushing the Docker images...',
              'docker push $REPOSITORY_URI:latest',
              'docker push $REPOSITORY_URI:$IMAGE_TAG',
              'echo Writing image definitions file...',
              'printf \'[{"name":"backend","imageUri":"%s"}]\' $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json',
            ],
          },
        },
        artifacts: {
          files: ['imagedefinitions.json'],
        },
      }),
      environmentVariables: {
        AWS_DEFAULT_REGION: {
          value: this.region,
        },
        AWS_ACCOUNT_ID: {
          value: this.account,
        },
      },
    });

    // Grant ECR permissions to CodeBuild
    ecrRepository.grantPullPush(backendBuildProject);

    // Frontend Build Project
    const frontendBuildProject = new codebuild.Project(this, 'FrontendBuild', {
      projectName: 'code-review-quest-frontend-build',
      source: codebuild.Source.codeCommit({
        repository: codebuild.Repository.gitHub({
          owner: 'your-github-username', // Replace with actual GitHub username
          repo: 'code-review-quest',
        }),
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        computeType: codebuild.ComputeType.SMALL, // Cost optimization
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          install: {
            'runtime-versions': {
              nodejs: '18',
            },
          },
          pre_build: {
            commands: [
              'cd frontend',
              'npm ci',
            ],
          },
          build: {
            commands: [
              'echo Build started on `date`',
              'npm run build',
            ],
          },
          post_build: {
            commands: [
              'echo Build completed on `date`',
            ],
          },
        },
        artifacts: {
          'base-directory': 'frontend/dist',
          files: ['**/*'],
        },
      }),
    });

    // ===========================================
    // CodePipeline
    // ===========================================
    const sourceOutput = new codepipeline.Artifact();
    const backendBuildOutput = new codepipeline.Artifact();
    const frontendBuildOutput = new codepipeline.Artifact();

    const pipeline = new codepipeline.Pipeline(this, 'Pipeline', {
      pipelineName: 'code-review-quest-pipeline',
      artifactBucket: artifactsBucket,
      stages: [
        {
          stageName: 'Source',
          actions: [
            new codepipeline_actions.GitHubSourceAction({
              actionName: 'GitHub_Source',
              owner: 'your-github-username', // Replace with actual GitHub username
              repo: 'code-review-quest',
              branch: 'main',
              oauthToken: cdk.SecretValue.secretsManager('github-token'), // Store GitHub token in Secrets Manager
              output: sourceOutput,
            }),
          ],
        },
        {
          stageName: 'Build',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Backend_Build',
              project: backendBuildProject,
              input: sourceOutput,
              outputs: [backendBuildOutput],
            }),
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Frontend_Build',
              project: frontendBuildProject,
              input: sourceOutput,
              outputs: [frontendBuildOutput],
            }),
          ],
        },
        {
          stageName: 'Deploy',
          actions: [
            new codepipeline_actions.EcsDeployAction({
              actionName: 'Backend_Deploy',
              service: ecs.FargateService.fromFargateServiceAttributes(this, 'ImportedService', {
                serviceName: 'code-review-quest-service',
                cluster: ecs.Cluster.fromClusterAttributes(this, 'ImportedCluster', {
                  clusterName: 'code-review-quest-cluster',
                  vpc: ec2.Vpc.fromLookup(this, 'ImportedVpc', {
                    vpcName: 'code-review-quest-vpc',
                  }),
                  securityGroups: [],
                }),
              }),
              input: backendBuildOutput,
            }),
            new codepipeline_actions.S3DeployAction({
              actionName: 'Frontend_Deploy',
              bucket: s3.Bucket.fromBucketName(this, 'ImportedFrontendBucket', 
                `code-review-quest-frontend-prod-${this.account}`),
              input: frontendBuildOutput,
            }),
          ],
        },
      ],
    });

    // ===========================================
    // Outputs
    // ===========================================
    new cdk.CfnOutput(this, 'ECRRepositoryURI', {
      value: ecrRepository.repositoryUri,
      description: 'ECR Repository URI',
    });

    new cdk.CfnOutput(this, 'PipelineName', {
      value: pipeline.pipelineName,
      description: 'CodePipeline name',
    });
  }
}
