from azure.identity import ClientSecretCredential
import os

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)

token = credential.get_token("https://management.azure.com/.default")
print("Azure Auth Success")
