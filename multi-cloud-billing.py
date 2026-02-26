import argparse
import os
import sys
from datetime import datetime

# AWS
import boto3

# GCP
from google.cloud import bigquery

# Azure
import requests
from azure.identity import ClientSecretCredential


# =====================================================
# AWS COST
# =====================================================
def get_aws_cost(start_date, end_date):
    try:
        client = boto3.client('ce')

        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )

        amount = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        unit = response['ResultsByTime'][0]['Total']['UnblendedCost']['Unit']

        return float(amount), unit

    except Exception as e:
        print(f"AWS Error: {e}")
        return 0.0, "USD"


# =====================================================
# GCP COST
# =====================================================
def get_gcp_cost(start_date, end_date, project_id, dataset):
    try:
        client = bigquery.Client(project=project_id)

        query = f"""
        SELECT IFNULL(SUM(cost), 0) as total_cost
        FROM `{project_id}.{dataset}.gcp_billing_export_v1_*`
        WHERE usage_start_time BETWEEN '{start_date}' AND '{end_date}'
        """

        result = client.query(query).result()

        for row in result:
            return float(row.total_cost), "₹"

        return 0.0, "₹"

    except Exception as e:
        print(f"GCP Error: {e}")
        return 0.0, "₹"


# =====================================================
# AZURE COST
# =====================================================
def get_azure_cost(start_date, end_date):
    try:
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

        if not all([tenant_id, client_id, client_secret, subscription_id]):
            raise Exception("Azure environment variables not set properly.")

        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        token = credential.get_token("https://management.azure.com/.default").token

        url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2021-10-01"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "timePeriod": {
                "from": start_date,
                "to": end_date
            },
            "dataset": {
                "granularity": "None",
                "aggregation": {
                    "totalCost": {
                        "name": "PreTaxCost",
                        "function": "Sum"
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception(f"Azure API Error: {response.text}")

        data = response.json()

        rows = data.get("properties", {}).get("rows", [])

        if not rows:
            return 0.0, "₹"

        cost = rows[0][0]

        return float(cost), "₹"

    except Exception as e:
        print(f"Azure Error: {e}")
        return 0.0, "₹"


# =====================================================
# MAIN
# =====================================================
def main():
    parser = argparse.ArgumentParser(description="Multi-Cloud Billing Report")

    parser.add_argument("--provider", required=True, choices=["aws", "gcp", "azure"])
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)

    args = parser.parse_args()

    print("\n========== Billing Report ==========")
    print(f"Provider : {args.provider.upper()}")
    print(f"Start    : {args.start_date}")
    print(f"End      : {args.end_date}")

    if args.provider == "aws":
        cost, unit = get_aws_cost(args.start_date, args.end_date)

    elif args.provider == "gcp":
        project_id = "mydemo-project-25487906-p5"
        dataset = "billing_export_dataset"
        cost, unit = get_gcp_cost(args.start_date, args.end_date, project_id, dataset)

    elif args.provider == "azure":
        cost, unit = get_azure_cost(args.start_date, args.end_date)

    print(f"Total    : {cost:.2f} {unit}")
    print("====================================\n")


if __name__ == "__main__":
    main()
