import boto3
from datetime import datetime, date

# Create Cost Explorer client
client = boto3.client('ce', region_name='us-west-2')

# Get today's date
today = date.today()

# First day of current month
start_date = today.replace(day=1)

# Convert to string format
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = today.strftime('%Y-%m-%d')

# Get cost and usage
response = client.get_cost_and_usage(
    TimePeriod={
        'Start': start_date_str,
        'End': end_date_str
    },
    Granularity='MONTHLY',
    Metrics=['UnblendedCost']
)

# Extract amount
amount = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
unit = response['ResultsByTime'][0]['Total']['UnblendedCost']['Unit']

# Display result
current_month = today.strftime('%B %Y')

print("\n========== AWS Billing Report ==========")
print(f"Month        : {current_month}")
print(f"Start Date   : {start_date_str}")
print(f"End Date     : {end_date_str}")
print(f"Total Cost   : {round(float(amount), 2)} {unit}")
print("========================================\n")
