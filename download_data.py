import kagglehub
import os

# Download the entire dataset
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

print(f"Dataset downloaded to: {path}")
print("\nFiles in dataset:")
for file in os.listdir(path):
    print(f"  - {file}")
