#!/usr/bin/env python3
"""
Keyword research script using Google Trends and estimation of volume/competition.
"""
import pandas as pd
from pytrends.request import TrendReq
import time
import random
from typing import List, Dict

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

def get_related_keywords(seed_keywords: List[str], max_results: int = 50) -> pd.DataFrame:
    """
    Get related keywords from Google Trends suggestions.
    Returns DataFrame with columns: keyword, type, value
    """
    all_keywords = []
    
    for seed in seed_keywords:
        try:
            # Get related queries
            pytrends.build_payload([seed], timeframe='today 12-m')
            related = pytrends.related_queries()
            
            if related[seed]['top'] is not None:
                top_df = related[seed]['top'].copy()
                top_df['seed'] = seed
                top_df['type'] = 'top'
                all_keywords.append(top_df)
            
            if related[seed]['rising'] is not None:
                rising_df = related[seed]['rising'].copy()
                rising_df['seed'] = seed
                rising_df['type'] = 'rising'
                all_keywords.append(rising_df)
                
            time.sleep(1)  # Be nice to Google
        except Exception as e:
            print(f"Error fetching keywords for '{seed}': {e}")
            continue
    
    if all_keywords:
        df = pd.concat(all_keywords, ignore_index=True)
        # Rename columns
        df.columns = ['keyword', 'value', 'seed', 'type']
        return df.head(max_results)
    else:
        return pd.DataFrame(columns=['keyword', 'value', 'seed', 'type'])

def estimate_search_volume(trend_value: int) -> int:
    """
    Rough estimation of monthly search volume based on trend value (0-100).
    This is a very rough approximation and should be calibrated with real data.
    """
    # Simple linear mapping: 100 trend ≈ 100,000 searches/month
    # Adjust based on your observations
    return int(trend_value * 1000)

def estimate_keyword_difficulty(keyword: str) -> float:
    """
    Estimate keyword difficulty (0-100) based on simple heuristics.
    In reality, you need SERP analysis or API data.
    This is a placeholder that returns random values for demonstration.
    """
    # Placeholder: random between 0-50 for low competition keywords
    # In production, replace with actual analysis (e.g., number of search results,
    # domain authority of top pages, etc.)
    return round(random.uniform(0, 30), 1)

def filter_keywords(df: pd.DataFrame, max_kd: float = 10, min_volume: int = 1000) -> pd.DataFrame:
    """
    Filter keywords based on estimated KD and volume.
    """
    filtered = []
    
    for _, row in df.iterrows():
        volume = estimate_search_volume(row['value'])
        kd = estimate_keyword_difficulty(row['keyword'])
        
        if kd <= max_kd and volume >= min_volume:
            filtered.append({
                'keyword': row['keyword'],
                'seed': row['seed'],
                'type': row['type'],
                'trend_value': row['value'],
                'estimated_volume': volume,
                'estimated_kd': kd
            })
    
    return pd.DataFrame(filtered)

def main():
    # Define seed niches
    seed_niches = [
        'health',
        'personal finance',
        'technology',
        'home improvement',
        'gardening',
        'cooking',
        'fitness',
        'travel',
        'education',
        'software'
    ]
    
    print("Starting keyword research...")
    print(f"Seed niches: {', '.join(seed_niches)}")
    
    # Get related keywords
    keywords_df = get_related_keywords(seed_niches, max_results=200)
    
    if keywords_df.empty:
        print("No keywords found. Check internet connection or try different seeds.")
        return
    
    print(f"Found {len(keywords_df)} related keywords.")
    
    # Filter by estimated KD <= 10 and volume >= 1000
    filtered_df = filter_keywords(keywords_df)
    
    print(f"Filtered to {len(filtered_df)} keywords with KD <= 10 and volume >= 1000.")
    
    # Sort by volume (descending)
    filtered_df = filtered_df.sort_values('estimated_volume', ascending=False)
    
    # Save results
    output_path = 'keywords/filtered_keywords.csv'
    filtered_df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    
    # Print top 20
    print("\nTop 20 keywords:")
    print(filtered_df[['keyword', 'estimated_volume', 'estimated_kd', 'seed']].head(20).to_string(index=False))
    
    # Analyze by niche
    print("\nKeywords per niche:")
    niche_counts = filtered_df.groupby('seed').size().sort_values(ascending=False)
    print(niche_counts.to_string())

if __name__ == '__main__':
    main()