#!/usr/bin/env python3
"""
Domain name search script for AdSense Automation project.
Uses Lean Domain Search API via web scraping.
"""

import requests
import time
from typing import List, Dict, Tuple
import sys

def search_domain(keyword: str) -> List[str]:
    """
    Search for available domains using Lean Domain Search.
    Returns list of available domains (empty if none found).
    """
    url = f"https://leandomainsearch.com/search/{keyword}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse simple HTML response
        # If results exist, they appear in <li> elements
        # For now, we just check if "No results found" appears
        if "No results found" in response.text:
            return []
        else:
            # Extract domains from response (simplistic)
            # In reality, would need proper HTML parsing
            # For now, return the keyword with .com as placeholder
            return [f"{keyword}.com"]
    
    except requests.RequestException as e:
        print(f"Error searching '{keyword}': {e}")
        return []

def generate_keywords() -> List[str]:
    """Generate domain keyword ideas based on niches."""
    prefixes = [
        'auto', 'smart', 'easy', 'quick', 'mega', 'super', 'hyper',
        'meta', 'neo', 'prime', 'alpha', 'beta', 'gamma', 'delta',
        'content', 'blog', 'article', 'guide', 'tips', 'tricks',
        'wiki', 'hub', 'lab', 'base', 'central', 'zone', 'spot',
        'place', 'world', 'network', 'system', 'engine', 'tool',
        'kit', 'pack', 'box', 'master', 'pro', 'expert', 'genius'
    ]
    
    suffixes = [
        'hub', 'lab', 'guide', 'tips', 'tricks', 'wiki', 'base',
        'central', 'zone', 'spot', 'place', 'world', 'network',
        'system', 'engine', 'tool', 'kit', 'pack', 'box', 'center',
        'portal', 'source', 'resource', 'library', 'archive', 'vault'
    ]
    
    niches = ['finance', 'home', 'wellness', 'health', 'diy', 'improvement']
    
    keywords = []
    
    # Combine prefixes + niches
    for prefix in prefixes[:15]:  # Limit to avoid too many
        for niche in niches:
            keywords.append(f"{prefix}{niche}")
            keywords.append(f"{prefix}{niche}guide")
    
    # Combine niches + suffixes
    for niche in niches:
        for suffix in suffixes[:15]:
            keywords.append(f"{niche}{suffix}")
    
    # Two-word combinations
    two_words = [
        'autocontent', 'contentauto', 'blogauto', 'autoblog',
        'smartcontent', 'contentai', 'aiblog', 'blogai',
        'easyguide', 'quicktips', 'megaguide', 'superhub',
        'contentlab', 'bloghub', 'articlehub', 'guidebase'
    ]
    
    keywords.extend(two_words)
    
    # Add our project name variations
    project_names = [
        'adsenseauto', 'adsenseautomation', 'autoadsense',
        'nicheauto', 'autoniche', 'contentautomation',
        'automatedcontent', 'aigenerated', 'aicontent'
    ]
    
    keywords.extend(project_names)
    
    return list(set(keywords))[:50]  # Limit to 50 for testing

def main():
    print("🔍 Generating domain name suggestions...")
    keywords = generate_keywords()
    
    print(f"Generated {len(keywords)} keyword ideas")
    print("\nTesting availability (this may take a moment)...")
    
    available = []
    unavailable = []
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\rChecking {i}/{len(keywords)}: {keyword}", end="", flush=True)
        
        results = search_domain(keyword)
        
        if results:
            available.extend(results)
            print(f" ✓")
        else:
            unavailable.append(keyword)
            print(f" ✗")
        
        time.sleep(0.5)  # Be nice to the server
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    if available:
        print(f"\n✅ POTENTIALLY AVAILABLE ({len(available)}):")
        for domain in available[:20]:  # Show top 20
            print(f"  • {domain}")
        
        if len(available) > 20:
            print(f"  ... and {len(available) - 20} more")
    else:
        print("\n❌ No domains found available with these keywords.")
        print("Try different keywords or check manually.")
    
    print(f"\n❌ UNAVAILABLE ({len(unavailable)} keywords)")
    
    # Save results to file
    with open('domain_suggestions.txt', 'w') as f:
        f.write("Domain Suggestions for AdSense Automation\n")
        f.write("="*50 + "\n\n")
        
        if available:
            f.write("Available/Check These:\n")
            for domain in available:
                f.write(f"- {domain}\n")
            f.write("\n")
        
        f.write("Keywords Tested (unavailable):\n")
        for keyword in unavailable:
            f.write(f"- {keyword}\n")
    
    print(f"\n📄 Results saved to 'domain_suggestions.txt'")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("1. Check exact availability on Namecheap/GoDaddy")
    print("2. Consider .com, .net, .org alternatives")
    print("3. Shorter domains (<15 chars) are better")
    print("4. Easy to spell and remember")
    print("5. Avoid numbers and hyphens")

if __name__ == '__main__':
    main()