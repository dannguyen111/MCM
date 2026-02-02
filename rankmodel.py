import pandas as pd
import numpy as np
from requests import head

def compute_phase1_results(file_path):
    # Load data
    df = pd.read_csv(file_path)
    
    # Clean column names (strip whitespace)
    df.columns = df.columns.str.strip().str.lower()
    
    weekly_results = []

    # Iterate through each season present in the data
    for season in df['season'].unique():
        season_df = df[df['season'] == season]
        
        # We need to detect how many weeks are in this season
        # We look for columns starting with "week" and containing "judge1"
        week_cols = [c for c in df.columns if c.startswith('week') and 'judge1' in c]
        # Extract week numbers (e.g. "week1_judge1..." -> 1)
        week_nums = sorted(list(set([int(c.split('_')[0].replace('week', '')) for c in week_cols])))
        
        for w in week_nums:
            # 1. Identify Active Contestants
            # Condition: Must have a valid score > 0 this week
            # (Eliminated contestants have 0s)
            score_col_1 = f'week{w}_judge1_score'
            if score_col_1 not in df.columns: continue
            
            # Filter for active dancers in this specific week
            active_dancers = season_df[season_df[score_col_1] > 0].copy()
            
            if active_dancers.empty:
                continue

            # 2. Calculate Total Judge Score
            # Sum all judge columns for this week (judge1 to judge4)
            judge_cols = [c for c in df.columns if c.startswith(f'week{w}_judge')]
            
            # Handle N/A by converting to 0 or ignoring (summing only valid scores)
            # The prompt implies N/A means no judge, so simple sum is fine
            active_dancers['weekly_judge_total'] = active_dancers[judge_cols].sum(axis=1)
            
            # 3. Compute Judge Rank
            # Method='average' (1.5, 1.5) or 'min' (1, 1, 3)? 
            # Prompt context suggests Average Rank is best for math models.
            # Ascending=False because Higher Score is Better (Rank 1)
            active_dancers['judge_rank'] = active_dancers['weekly_judge_total'].rank(ascending=False, method='average')
            
            # Store State
            for _, row in active_dancers.iterrows():
                weekly_results.append({
                    'Season': season,
                    'Week': w,
                    'Contestant': row['celebrity_name'],
                    'Judge_Total': row['weekly_judge_total'],
                    'Judge_Rank': row['judge_rank'],
                    'Result': row['results'] # Helpful to debug who went home
                })

    return pd.DataFrame(weekly_results)

# Usage
df_state = compute_phase1_results('Problem-C-dataset-rank-based.csv')
head(df_state)
# print(df_state[(df_state['Season'] == 1) & (df_state['Week'] == 2)])