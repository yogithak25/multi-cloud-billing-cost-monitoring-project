from google.cloud import bigquery
from google.cloud import resourcemanager_v3
from datetime import datetime
import sys

if len(sys.argv) != 2:
    print("\nUsage: python3 billing_report.py <project_name>\n")
    sys.exit(1)

project_name = sys.argv[1]

# Step 1: Find Project ID from Project Name
rm_client = resourcemanager_v3.ProjectsClient()
request = resourcemanager_v3.SearchProjectsRequest()

project_id = None

for project in rm_client.search_projects(request=request):
    if project.display_name == project_name:
        project_id = project.project_id
        break

if not project_id:
    print("\n❌ Error: Project name not found in GCP.\n")
    sys.exit(1)

# Step 2: Query Billing using Project ID
bq_client = bigquery.Client()

dataset_id = "billing_export_dataset"
billing_project = "mydemo-project-25487906-p5"

now = datetime.now()
month_name = now.strftime("%B")
year = now.year
month = now.month

query = f"""
SELECT
  SUM(cost) AS total_cost
FROM
  `{billing_project}.{dataset_id}.gcp_billing_export_resource_v1_*`
WHERE
  project.id = '{project_id}'
  AND EXTRACT(YEAR FROM usage_start_time) = {year}
  AND EXTRACT(MONTH FROM usage_start_time) = {month}
"""

query_job = bq_client.query(query)
results = query_job.result()

row = next(results)
total = row.total_cost or 0

print("\n==============================")
print(f"Project Name : {project_name}")
print(f"Project ID   : {project_id}")
print(f"Month        : {month_name} {year}")
print(f"Total Cost   : {total:.2f}")
print("==============================\n")
