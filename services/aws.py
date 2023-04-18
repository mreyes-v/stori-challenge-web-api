import boto3

aws_access_key_id='AKIAWIKKDOR2UVMZLWMV'
aws_secret_access_key='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'

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'
    )

s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'
)

ses = boto3.client(
    "ses",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'
)
