import os
import numpy as np
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_segmentation_data.csv"

def generate_data():
    np.random.seed(42)
    
    # Base configuration:
    # Enterprise: 300 customers
    # SMB: 300 customers
    # Startup: 400 customers
    
    segments = []
    
    # -----------------------------
    # 1. Enterprise Customers (300)
    # -----------------------------
    n_ent = 300
    ent_churn = np.array([0] * 297 + [1] * 3) # 1% churn (3/300)
    np.random.shuffle(ent_churn)
    
    for i in range(n_ent):
        segments.append({
            'customer_type': 'Enterprise',
            'lifetime_value': np.random.normal(150000, 20000),
            'churn': ent_churn[i],
            'support_tickets': np.random.normal(8.5, 1.5),
            'retention_days': np.random.normal(720, 60)
        })
        
    # -----------------------------
    # 2. SMB Customers (300)
    # -----------------------------
    n_smb = 300
    smb_churn = np.array([0] * 264 + [1] * 36) # 12% churn (36/300)
    np.random.shuffle(smb_churn)
    
    for i in range(n_smb):
        segments.append({
            'customer_type': 'SMB',
            'lifetime_value': np.random.normal(8000, 1500),
            'churn': smb_churn[i],
            'support_tickets': np.random.normal(4.2, 1.2),
            'retention_days': np.random.normal(360, 45)
        })
        
    # -----------------------------
    # 3. Startup Customers (400)
    # -----------------------------
    n_su = 400
    su_churn = np.array([0] * 369 + [1] * 31) # 7.75% churn ~ 8% (31/400)
    np.random.shuffle(su_churn)
    
    for i in range(n_su):
        segments.append({
            'customer_type': 'Startup',
            'lifetime_value': np.random.normal(2000, 500),
            'churn': su_churn[i],
            'support_tickets': np.random.normal(1.5, 0.8),
            'retention_days': np.random.normal(240, 30)
        })
        
    df = pd.DataFrame(segments)
    
    # Scale variables to reasonable positive constraints
    df['lifetime_value'] = df['lifetime_value'].clip(lower=100).round(2)
    df['support_tickets'] = df['support_tickets'].clip(lower=0).round(0).astype(int)
    df['retention_days'] = df['retention_days'].clip(lower=1).round(0).astype(int)
    
    # Shuffle the dataset so rows are mixed
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.insert(0, 'customer_id', range(1001, 1001 + len(df)))
    
    # Ensure directory exists
    os.makedirs(RAW_DATA.parent, exist_ok=True)
    
    # Save CSV
    df.to_csv(RAW_DATA, index=False)
    print(f"Success: Generated raw dataset saved to: {RAW_DATA}")
    
    # Verify aggregate metrics
    print(f"Total customers: {len(df)}")
    print(f"Aggregate Churn Rate: {df['churn'].mean():.2%}")
    print("\nMetrics per Segment:")
    print(df.groupby('customer_type').agg({
        'lifetime_value': 'mean',
        'churn': 'mean',
        'support_tickets': 'mean',
        'retention_days': 'mean',
        'customer_id': 'count'
    }))

if __name__ == "__main__":
    generate_data()
