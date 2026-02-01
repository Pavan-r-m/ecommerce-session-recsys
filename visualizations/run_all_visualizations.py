"""
Master script to run all visualization scripts
"""

import os
import sys
import subprocess

# Create outputs directory if it doesn't exist
os.makedirs('visualizations/outputs', exist_ok=True)

print("=" * 70)
print("RUNNING ALL E-COMMERCE ANALYTICS VISUALIZATIONS")
print("=" * 70)

visualization_scripts = [
    ('Customer Segmentation', 'visualizations/customer_segmentation_viz.py'),
    ('Geographic Analysis', 'visualizations/geographic_analysis_viz.py'),
    ('Time Series & Trends', 'visualizations/time_series_viz.py'),
    ('Product Analysis', 'visualizations/product_analysis_viz.py'),
    ('Delivery & Payment', 'visualizations/delivery_payment_viz.py')
]

total_scripts = len(visualization_scripts)
completed = 0
failed = 0

for name, script in visualization_scripts:
    print(f"\n{'=' * 70}")
    print(f"Running: {name}")
    print(f"{'=' * 70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        completed += 1
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {name}:")
        print(e.stdout)
        print(e.stderr)
        failed += 1
    except Exception as e:
        print(f"❌ Unexpected error in {name}: {str(e)}")
        failed += 1

print(f"\n{'=' * 70}")
print("VISUALIZATION GENERATION COMPLETE")
print(f"{'=' * 70}")
print(f"Total Scripts: {total_scripts}")
print(f"✅ Completed: {completed}")
print(f"❌ Failed: {failed}")
print(f"\nAll visualizations saved to: visualizations/outputs/")
print(f"{'=' * 70}\n")
