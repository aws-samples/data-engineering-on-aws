This solution talks about how we can derive insights from transactional data residing in RDS MySQL by exporting the data to S3 and building ML model  using Redshift ML without building complex ETL pipelines and not disrupting the source RDS database. The use case considered for this solution is the Bank Marketing data from https://archive.ics.uci.edu/ml/datasets/bank+marketing. This is a classification problem, where the goal is to predict if the customer will  subscribe to a term deposit or not.

The solution leverages the training and inference datasets of the following Redshift Immersion Lab: https://catalog.workshops.aws/redshift-immersion/en-US/lab17a

Prerequisites: 
1/ Create IAM role with read and write access to S3. Attach it to the Redshift cluster. More details at https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ExportSnapshot.html#USER_ExportSnapshot.SetupIAMRole.

2/ Create a symmetric encryption AWS KMS key for the server-side encryption. The KMS key will be used by the snapshot export task to set up AWS KMS server-side encryption when writing the export data to S3. The KMS key policy must include both the kms:Encrypt and kms:Decrypt permissions. More details at https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ExportSnapshot.html.

3/ Create two RDS MySQL tables, one each for training and inference. For detailed steps on how to create RDS MySQL instance and connect using SQL client, please refer https://aws.amazon.com/getting-started/hands-on/create-mysql-db/.

Table definition of training data:

CREATE TABLE <db_name>.<training_table_name>(
   age numeric,
   jobtype char (25),
   marital char (25),
   education char (25),
   default_col char (25),
   housing char (25),
   loan char (25),
   contact char (25),
   month char (25),
   day_of_week char (25),
   duration numeric,
   campaign numeric,
   pdays numeric,
   previous numeric,
   poutcome char (25),
   emp_var_rate numeric,
   cons_price_idx numeric,     
   cons_conf_idx numeric,     
   euribor3m numeric,
   nr_employed numeric,
   y char(1) ) ;
   
Table definition of inference data:   

CREATE TABLE <db_name>.<inference_table_name>(
   age numeric,
   jobtype char (25),
   marital char (25),
   education char (25),
   default_col char (25),
   housing char (25),
   loan char (25),
   contact char (25),
   month char (25),
   day_of_week char (25),
   duration numeric,
   campaign numeric,
   pdays numeric,
   previous numeric,
   poutcome char (25),
   emp_var_rate numeric,
   cons_price_idx numeric,     
   cons_conf_idx numeric,     
   euribor3m numeric,
   nr_employed numeric,
   y char(1) ) ;

4/ Load sample data in RDS MySQL 
LOAD DATA LOCAL INFILE '<path to train_data.csv>' INTO TABLE steps.train FIELDS TERMINATED BY ',' ignore 1 lines;

LOAD DATA LOCAL INFILE '<path to inference_part1.csv' INTO TABLE test.bank_details_inference FIELDS TERMINATED BY ',' ignore 1 lines;
LOAD DATA LOCAL INFILE '<path to inference_part2.csv' INTO TABLE test.bank_details_inference FIELDS TERMINATED BY ',';
LOAD DATA LOCAL INFILE '<path to inference_part3.csv' INTO TABLE test.bank_details_inference FIELDS TERMINATED BY ',';
LOAD DATA LOCAL INFILE '<path to inference_part4.csv' INTO TABLE test.bank_details_inference FIELDS TERMINATED BY ',';

5/ Validate the data by doing select * on the newly loaded tables via. SQL client or EC2 connect.

6/ Create Redshift provisioned cluster (RA3 2 node cluster preferred) or Redshift serverless endpoint (leave all to default). More details at https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-sample-data-load-create-cluster.html (cluster).

Solution execution steps:
In this solution, the data from two tables created above will be exported to S3 by taking a manual snapshot of the RDS DB instance and exporting it to S3. Post that, the data will be copied to Redshift for adding a new row number column. This column will be used for selecting a subset of records from the training table for creating the model. This can be extended for other use cases such as joining with other tables, deriving new columns etc.

1/ Navigate to RDS console, select the database instance and take DB Snapshot by selecting the database and choose Actions > Take snapshot

2/ Once the snapshot is created, select the snapshot and export to S3 by selecting the snapshot choose Actions > Export to Amazon S3
   2.a/ If only the training and inference tables to be exported to S3, please choose 'Partial' under 'Exported data' section. In the box below, enter the names of the tables in the format schema.table_name separated by space
   2.b/ Choose the appropriate bucket or create new one.
   2.c/ Choose the appropriate IAM role that has write access to the above S3 bucket.
   2.d/ Choose the appropriate KMS key created in prerequisites.

3/ Navigate to Redshift console and choose the Redshift provisioned cluster/serverless namespace created in prerequisites. Click 'Query data' button and 'Query in query editor v2'.

4/ Create new notebook and import the sample notebook given.

5/ Run cell by cell and follow the instructions given in the comments of each cell. (For model training, it will take about an hour).

6/ Once the notebook is run, please delete the following resources to save costs: 1/ Redshift cluster/serverless endpoint; 2/ RDS DB instance; 3/ Snapshots; 4/ S3 data exported; 5/ EC2 instance (if used for RDS connect).
