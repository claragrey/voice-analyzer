import os

# Set the environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\Work\KYRO\Project\va_deployment\voice_analyzer1_gem\project-d7-65-50c13423c1af.json"

# Verify it is set
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
