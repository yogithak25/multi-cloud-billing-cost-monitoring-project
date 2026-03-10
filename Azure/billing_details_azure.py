from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient
from datetime import datetime, timezone

# ----------------------------
# SUBSCRIPTION ID
# ----------------------------
subscription_id = "80e8ae92-8bcc-4a2a-8c20-74732981ca82"

# ----------------------------
# AUTHENTICATION
# ----------------------------
credential = DefaultAzureCredential()
client = ConsumptionManagementClient(credential, subscription_id)

scope = f"/subscriptions/{subscription_id}"

# ----------------------------
# CURRENT MONTH & YEAR
# ----------------------------
now = datetime.now(timezone.utc)
current_month = now.month
current_year = now.year

total_cost = 0.0

# ----------------------------
# FETCH USAGE DETAILS
# ----------------------------
usage_details = client.usage_details.list(scope=scope)

for item in usage_details:
    # ModernUsageDetail commonly uses 'date'
    usage_date = getattr(item, "date", None)

    if usage_date and usage_date.month == current_month and usage_date.year == current_year:
        # Try multiple possible cost fields
        cost = (
            getattr(item, "cost_in_billing_currency", None) or
            getattr(item, "pretax_cost", None) or
            getattr(item, "cost", 0)
        )

        total_cost += float(cost)

# ----------------------------
# OUTPUT
# ----------------------------
print("\n====================================")
print("        AZURE BILLING SUMMARY")
print("====================================")
print("Month          :", now.strftime("%B"))
print("Year           :", current_year)
print("Total Cost     :", round(total_cost, 2), "₹")
print("====================================\n")
