import pandas as pd

# Load sample keywords
df = pd.read_csv('keywords/sample_keywords.csv')

# Filter: KD <= 10, Search Volume >= 1000
filtered = df[(df['kd'] <= 10) & (df['search_volume'] >= 1000)]

# Sort by search volume descending
filtered = filtered.sort_values('search_volume', ascending=False)

print(f"Total keywords: {len(df)}")
print(f"Filtered keywords: {len(filtered)}")
print("\nFiltered keywords:")
print(filtered[['keyword', 'niche', 'search_volume', 'kd', 'cpc']].to_string(index=False))

# Save to CSV
filtered.to_csv('keywords/filtered_sample.csv', index=False)
print(f"\nSaved to keywords/filtered_sample.csv")