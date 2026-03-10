from google.cloud import bigquery
from google.cloud import resourcemanager_v3
from datetime import datetime
import sys

if len(sys.argv) != 4:
    print("Usage: python3 billing-det.py <project_name> <start_date> <end_date>")
    #print("Example: python3 billing-det.py demo-project 2026-02-01 2026-02-20")
    sys.exit(1)

project_name = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

# Convert project name to project ID
rm_client = resourcemanager_v3.ProjectsClient()
projects = rm_client.search_projects(query=f"displayName={project_name}")

project_id = None
for p in projects:
    project_id = p.project_id
    break

if not project_id:
    print("❌ Error: Project does not exist")
    sys.exit(1)

bq_client = bigquery.Client()

billing_project = "mydemo-project-25487906-p5"
dataset = "billing_export_dataset"
table = "gcp_billing_export_resource_v1_*"

query = f"""
SELECT
  SUM(cost) AS total_cost
FROM
  `{billing_project}.{dataset}.{table}`
WHERE
  project.id = '{project_id}'
  AND usage_start_time BETWEEN TIMESTAMP('{start_date}')
  AND TIMESTAMP('{end_date}')
"""

query_job = bq_client.query(query)
results = query_job.result()

for row in results:
    total = row.total_cost or 0
    print("\n==============================")
    print(f"Project Name : {project_name}")
    print(f"Project ID   : {project_id}")
    print(f"Start Date   : {start_date}")
    print(f"End Date     : {end_date}")
    print(f"Total Cost   : {total:.2f}")
    print("==============================\n")
