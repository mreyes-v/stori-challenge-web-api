# Stori transactions - challenge

## Project summary

The project consist of two modules:

1. Web-API
2. Lambda Function

### WEB - API

This repo corresponds to the Web-API, which contain endpoints to `get` and `insert` transactions, and an `upload`
endpoint is provided to upload a .csv file to an S3 Bucket with a very simple web interface.

The `insert` endpoint receives json data and inserts it into an DynamoDB Table. It can receive a list of transactions
or a single object with a single transaction. After successfully insert data in DynamoDB, all data is retrieved to
compute the summary and send the information via email using the AWS SES.

The `get` endpoint receives json data and inserts it into an DynamoDB Table. If the paraneter `id` is provided in the
URL, it will return a single object if the id exists. If no `ìd` parameter is provided, it will return a list of all
the transactions in DynamoDB.

The `upload` endpoint renders a simple web page to upload a .csv file. Once it is uploaded to S3 Bucket a Lambda
Function is triggered, the lambda function will read the .csv file from the S3 Bucket, parse it, and insert the
transactions into DynamoDB. After the insertion, all the data from DynamoDB will be retrieved and the summary will be
computed to sent it via email using AWS SES.

## Run the Web-API

The easiest way to run the project is using Docker:
```
docker build --tag stori-web-api .
docker run -p 5002:5001 stori-web-api
```

Now you can go to http://localhost:5002/transactions/upload to upload a .csv file or use the provided Postman
collection to test the endpoints.

__Important__: AWS keys cannot be provided in the repo, please ask for them if needed.