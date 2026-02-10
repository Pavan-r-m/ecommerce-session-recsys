#!/bin/bash
# Training Pipeline Script
# Run this to train all models from scratch

set -e  # Exit on error

echo "===================================="
echo "E-Commerce Recommender Training Pipeline"
echo "===================================="

# Check if in correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Run this script from project root"
    exit 1
fi

# Create artifacts directory
mkdir -p src/artifacts

echo ""
echo "[Step 1/3] Building training dataset..."
python -m src.training.build_dataset

echo ""
echo "[Step 2/3] Training baseline models (item-to-item)..."
python -m src.training.train_baselines

echo ""
echo "[Step 3/3] Training LightGBM ranker..."
python -m src.training.train_ranker

echo ""
echo "===================================="
echo "✅ Training complete!"
echo "===================================="
echo ""
echo "Artifacts saved to: src/artifacts/"
ls -lh src/artifacts/

echo ""
echo "Next steps:"
echo "  1. Review metrics above"
echo "  2. Start API: docker compose up"
echo "  3. Test: curl http://localhost:8000/health"
