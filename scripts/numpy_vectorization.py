import pandas as pd
import numpy as np
import time
from pathlib import Path

# --------------------------------------------------------
# Project Paths
# --------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "revenue_vectorization_data.csv"

OUTPUT_FILE = BASE_DIR / "data" / "processed" / "revenue_vectorized.csv"

print("=" * 70)
print("NUMPY VECTORISED COMPUTATION WORKFLOW")
print("=" * 70)

# --------------------------------------------------------
# Load Dataset
# --------------------------------------------------------

df = pd.read_csv(RAW_FILE)

print("\nDataset")
print(df)

# --------------------------------------------------------
# TASK 1
# Loop Normalization
# --------------------------------------------------------

print("\nTask 1 : Loop Normalization")

loop_normalized = []

minimum = df["Revenue"].min()
maximum = df["Revenue"].max()

for value in df["Revenue"]:
    norm = (value - minimum) / (maximum - minimum)
    loop_normalized.append(norm)

# --------------------------------------------------------
# NumPy Vectorization
# --------------------------------------------------------

print("Task 1 : NumPy Vectorization")

revenue = df["Revenue"].values

numpy_normalized = (revenue - revenue.min()) / (
    revenue.max() - revenue.min()
)

df["Revenue_Normalized"] = numpy_normalized

# --------------------------------------------------------
# TASK 2
# Z Score
# --------------------------------------------------------

print("\nTask 2 : Z Score")

z_scores = (revenue - revenue.mean()) / revenue.std()

df["Revenue_ZScore"] = z_scores

# --------------------------------------------------------
# TASK 3
# Revenue Ranking
# --------------------------------------------------------

print("\nTask 3 : Revenue Ranking")

ranking = np.argsort(-revenue)

ranks = np.empty_like(ranking)

ranks[ranking] = np.arange(1, len(ranking) + 1)

df["Revenue_Rank"] = ranks

# --------------------------------------------------------
# TASK 4
# Performance Comparison
# --------------------------------------------------------

print("\nTask 4 : Performance Comparison")

start = time.time()

result_loop = []

for value in df["Revenue"]:
    result_loop.append(value * 1.10)

loop_time = time.time() - start

start = time.time()

result_numpy = revenue * 1.10

numpy_time = time.time() - start

print(f"Loop Time  : {loop_time:.8f} sec")
print(f"NumPy Time : {numpy_time:.8f} sec")

if numpy_time > 0:
    print(f"Speedup : {loop_time / numpy_time:.2f}x")

# --------------------------------------------------------
# TASK 5
# Integrate Back to DataFrame
# --------------------------------------------------------

df["Revenue_Plus10"] = result_numpy

print("\nUpdated Dataset")

print(df)

print("\nShape")

print(df.shape)

print("\nData Types")

print(df.dtypes)

# --------------------------------------------------------
# Save
# --------------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\nVectorized dataset saved successfully.")

print(OUTPUT_FILE)