import json
from datetime import datetime, timezone

import boto3

securityhub = boto3.client("securityhub")


def lambda_handler(event, context):
    finding = event["detail"]["findings"][0]

    finding_id = finding["Id"]
    product_arn = finding["ProductArn"]

    note_text = (
        "LAB07 automated response executed via EventBridge + Lambda at "
        f"{datetime.now(timezone.utc).isoformat()}"
    )

    response = securityhub.batch_update_findings(
        FindingIdentifiers=[
            {
                "Id": finding_id,
                "ProductArn": product_arn,
            }
        ],
        Workflow={"Status": "NOTIFIED"},
        Note={
            "Text": note_text,
            "UpdatedBy": "lab07-response-lambda",
        },
    )

    unprocessed = response.get("UnprocessedFindings", [])
    if unprocessed:
        # A returned error must fail the invocation so Lambda can retry it.
        raise RuntimeError(f"Security Hub did not update the finding: {unprocessed}")

    print(
        json.dumps(
            {
                "finding_id": finding_id,
                "product_arn": product_arn,
                "workflow_status": "NOTIFIED",
            }
        )
    )

    return {
        "ok": True,
        "finding_id": finding_id,
    }
