from __future__ import print_function
from aws_kinesis_agg.deaggregator import iter_deaggregate_records
from datetime import datetime
import base64
import json
import boto3
import os

# OS input variables:
cloudwatch_namespace = os.environ['cloudwatch_namespace']
cloudwatch_metric = os.environ['cloudwatch_metric']
dynamodb_control_table = os.environ['dynamodb_control_table']
topic_arn = os.environ['topic_arn']

# AWS Services
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
db_table = dynamodb.Table(dynamodb_control_table)


def lambda_handler(event, context):
    raw_kinesis_records = event['Records']
    record_count = 0

    # Using DynamoDB Batch Writer. Source: http://bit.ly/2ZSSdIz
    with db_table.batch_writer() as batch_writer:

        # Deaggregate all records using a generator function
        for record in iter_deaggregate_records(raw_kinesis_records):

            try:
                # Kinesis data in Python Lambdas is base64 encoded
                payload = base64.b64decode(record['kinesis']['data'])
                json_document = json.loads(payload.decode('utf-8'))

                # Input Data extraction
                input_user_id = str(json_document['user_id'])
                input_num_actions_per_watermark = str(json_document['num_actions_per_watermark'])

                # DYNAMODB LAYER:
                # - Add time as Monitor Control and Write micro-batch to DynamoDB:
                json_document['ddb_partition_key'] = 'userid#{}#appserver#{}'.format(input_user_id, 'app-server-tomcat-123')
                json_document['ddb_sort_key'] = int(datetime.utcnow().timestamp())
                ddb_response = batch_writer.put_item(Item=json_document)
                print('DynamoDB API Response: {}'.format(ddb_response))

                # CLOUDWATCH LAYER:
                # - Note: this can be dynamically built or fetched from properties file,
                #         without hard-coding KEY-VALUE pairs.
                dimension_name_1 = 'user_id'
                dimension_name_2 = 'num_actions_per_watermark'
                cloudwatch_response = cloudwatch.put_metric_data(
                    MetricData=[
                        {
                            'MetricName': cloudwatch_metric,
                            'Dimensions': [
                                {
                                    'Name': dimension_name_1,
                                    'Value': input_user_id
                                },
                                {
                                    'Name': dimension_name_2,
                                    'Value': input_num_actions_per_watermark
                                },
                            ],
                            'Unit': 'Count',
                            'Value': 1,
                            'StorageResolution': 1
                        },
                    ],
                    Namespace=cloudwatch_namespace
                )

                # Print Cloudwatch response:
                # - Implement real Logging for Production; e.g. logging.getLogger().setLevel(logging.INFO)
                print('CloudWatch API Response: {}'.format(cloudwatch_response))

                # DDoS NOTIFICATIONS LAYER: Look for possible BOTs or attacks in stream:
                if int(input_num_actions_per_watermark) > 10:
                    sns_response = sns.publish(TopicArn=topic_arn, Message=str(json_document),
                                               Subject='Possible DDoS detected, by user_id {} with a number of attempts of : {}/window'.format(input_user_id, input_num_actions_per_watermark))
                    print('Email notification sent, due high severity incident. API Response: {}'.format(sns_response))

            except Exception as e:
                # - Implement real Logging for Production; e.g. logging.getLogger().setLevel(logging.INFO)
                print('Error when processing stream:')
                print(e)

            # Print response and increment counter
            record_count += 1

    return 'Successfully processed {} records.'.format(record_count)
