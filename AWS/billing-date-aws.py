import boto3

client = boto3.client('ce', region_name='us-west-2')

start_date = "2025-12-01"
end_date = "2026-01-01"   # End date is exclusive (next day)

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

print("\n===== AWS Custom Date Billing Report=====")
print("From :", start_date)
print("To   :", end_date)
print("Cost :", round(float(amount), 2), unit)
print("====================================\n")
