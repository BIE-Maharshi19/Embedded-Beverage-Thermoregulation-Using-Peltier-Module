# MongoDB Logger Lambda Function

This Lambda function processes incoming AWS IoT messages and logs them to a MongoDB Atlas database. It supports two types of topics:
- `siploma/user/input`
- `siploma/performance`

## 1. Environment Settings

The following environment variables must be configured for the Lambda function:

| Variable Name         | Description                                           |
|-----------------------|-------------------------------------------------------|
| `username`            | MongoDB Atlas database username                      |
| `password`            | MongoDB Atlas database password                      |
| `cluster`             | MongoDB cluster name (e.g., `cluster0`)              |
| `database`            | Name of the MongoDB database                         |
| `input_collection`    | Collection name for user input logs                  |
| `performance_collection` | Collection name for performance logs            |

## 2. How to Run the Code

This Lambda function is intended to be triggered by an event from AWS IoT. Deploy it using the AWS Lambda Console or Infrastructure as Code (e.g., AWS CDK, Terraform) with the appropriate permissions and environment variables set.

**IAM Permissions Required:**
- Read environment variables
- CloudWatch logging

**Trigger:**
- AWS IoT Rule forwarding JSON message events to Lambda

## 3. How to Interpret the Results

Based on the incoming `event['topic']`, the Lambda does the following:

### Topic: `siploma/user/input`
- Inserts a document into the input collection with:
  - `timestamp`
  - `session_id`
  - `target_temp`
  - `source`

### Topic: `siploma/performance`
- Inserts a document into the performance collection based on `user_action`:
  - **SET**: Includes `session_id`, `user_action`, `mode`, `timestamp`, `drink_temp`, `target_temp`, `source`
  - **STOP**: Includes `session_id`, `user_action`, `mode`, `timestamp`, `source`

### Success Response:
```json
{
  "statusCode": 200,
  "body": "\"Insertion Successful!\""
}
```

### Error Response (Authentication Failure):
```json
{
  "statusCode": 401,
  "body": "\"Authentication Failed\""
}
```

## 4. Sample Input and Output

### Input Example (`siploma/user/input`):
```json
{
  "topic": "siploma/user/input",
  "session_id": "session123",
  "target_temp": 42,
  "timestamp": "2025-04-14 14:22:00",
  "source": "lambda_test_function"
}
```

### Output Document in MongoDB:
```json
{
  "timestamp": "2025-04-14 14:22:00",
  "session_id": "session123",
  "target_temp": 42,
  "source": "lambda_test_function"
}
```

### Input Example (`siploma/performance`):
```json
{
  "topic": "siploma/performance",
  "session_id": "session123",
  "user_action": "SET",
  "mode": "HEATING",
  "timestamp": "2025-04-14 14:23:00",
  "drink_temp": 38.5,
  "target_temp": 42,
  "source": "lambda_test_function"
}
```

### Output Document in MongoDB:
```json
{
  "session_id": "session123",
  "user_action": "SET",
  "mode": "HEATING",
  "timestamp": "2025-04-14 14:23:00",
  "drink_temp": 38.5,
  "target_temp": 42,
  "source": "lambda_test_function"
}
```

## 5. Additional Notes
- Ensure the Lambda function is deployed in a VPC with internet access or VPC peering if necessary to connect to MongoDB Atlas.
- MongoDB Atlas IP Whitelisting must include the public IPs used by Lambda (via NAT Gateway or VPC endpoints).
- Logs can be monitored via Amazon CloudWatch for debugging.
- Supports MongoDB server API version 1 for compatibility.

---

For further details, refer to [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/) and [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/).