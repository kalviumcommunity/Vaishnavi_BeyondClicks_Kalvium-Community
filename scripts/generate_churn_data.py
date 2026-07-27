import os
import numpy as np
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw" / "customer_churn_data.csv"

def generate_data():
    np.random.seed(994)
    n = 100
    
    # 1. Generate engagement
    engagement = np.random.normal(55, 15, n).clip(10, 100)
    
    # 2. Generate transactions_per_month with 0.92 correlation to engagement
    r_eng_tx = 0.92
    noise_tx = np.random.normal(0, 1, n)
    eng_std = (engagement - engagement.mean()) / engagement.std()
    tx_std = r_eng_tx * eng_std + np.sqrt(1 - r_eng_tx**2) * noise_tx
    transactions_per_month = (tx_std * 4 + 10).clip(1, 25)
    
    # 3. Generate churn
    churn = np.array([0] * 50 + [1] * 50)
    np.random.shuffle(churn)
    
    # 4. Generate support_tickets
    support_tickets = np.zeros(n)
    for i in range(n):
        if churn[i] == 1:
            support_tickets[i] = np.random.normal(6.5, 2.0)
        else:
            support_tickets[i] = np.random.normal(2.5, 2.0)
            
    support_tickets = np.round(support_tickets).clip(0, 10).astype(int)
    
    df = pd.DataFrame({
        'customer_id': range(1, n + 1),
        'engagement': np.round(engagement, 2),
        'transactions_per_month': np.round(transactions_per_month, 2),
        'support_tickets': support_tickets,
        'churn': churn
    })
    
    # Ensure raw directory exists
    os.makedirs(RAW_DATA.parent, exist_ok=True)
    
    # Save to file
    df.to_csv(RAW_DATA, index=False)
    print(f"Success: Generated raw dataset saved to {RAW_DATA}")
    
    # Verify correlations
    print("\nPearson Correlation in generated data:")
    print(df[['engagement', 'transactions_per_month', 'support_tickets', 'churn']].corr(method='pearson'))

if __name__ == "__main__":
    generate_data()
