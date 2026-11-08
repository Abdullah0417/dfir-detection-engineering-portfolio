CREATE EXTERNAL TABLE IF NOT EXISTS gd_logs (
  schemaversion string,
  accountid string,
  region string,
  partition string,
  id string,
  arn string,
  type string,
  resource string,
  service string,
  severity string,
  createdat string,
  updatedat string,
  title string,
  description string
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
-- Replace the bucket name and example account ID with your own export location.
LOCATION 's3://example-guardduty-findings/AWSLogs/111122223333/GuardDuty/'
TBLPROPERTIES ('has_encrypted_data'='true');
