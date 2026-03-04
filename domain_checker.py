#!/usr/bin/env python3
"""
Domain availability checker using whois.com
"""

import requests
import time
import sys
from typing import Optional

def check_domain_availability(domain: str) -> Optional[bool]:
    """
    Check if a domain is registered using whois.com.
    Returns:
        True if available (not registered)
        False if registered
        None if error/unknown
    """
    url = f"https://www.whois.com/whois/{domain}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        
        # Check for registration indicators
        if "Registered On" in html:
            # Extract registration date for debugging
            # Simple parsing - look for "Registered On:" pattern
            import re
            match = re.search(r'Registered On:\s*(\d{4}-\d{2}-\d{2})', html)
            if match:
                reg_date = match.group(1)
                print(f"  Registered on: {reg_date}")
            return False  # Registered
        
        # Check for "No match" or similar (not reliable for whois.com)
        elif "Domain not found" in html or "No match" in html:
            return True  # Possibly available
        
        # Check for generic landing page (might mean domain not in their database)
        elif "Leading provider of web presence solutions" in html:
            # This often appears for unregistered domains
            return True  # Possibly available
        
        else:
            # Unknown state
            return None
    
    except requests.RequestException as e:
        print(f"  Error checking {domain}: {e}")
        return None

def main():
    # Test domains
    test_domains = [
        # Known registered
        "google.com",
        "facebook.com",
        # Known likely registered
        "autocontent.com",
        "contentautomation.com",
        # New suggestions
        "autocontentlab.com",
        "contentaihub.com",
        "blogautomation.dev",
        "nicheautomator.net",
    ]
    
    print("🔍 Checking domain availability...")
    print("="*60)
    
    results = []
    
    for domain in test_domains:
        print(f"\nChecking {domain}...")
        
        # Rate limiting
        time.sleep(1)
        
        available = check_domain_availability(domain)
        
        if available is True:
            status = "✅ AVAILABLE (check manually)"
            results.append((domain, True))
        elif available is False:
            status = "❌ REGISTERED"
            results.append((domain, False))
        else:
            status = "⚠️  UNKNOWN (check manually)"
            results.append((domain, None))
        
        print(f"  Result: {status}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    available_domains = [d for d, avail in results if avail is True]
    registered_domains = [d for d, avail in results if avail is False]
    unknown_domains = [d for d, avail in results if avail is None]
    
    if available_domains:
        print(f"\n✅ Potentially Available ({len(available_domains)}):")
        for domain in available_domains:
            print(f"  • {domain}")
    
    if registered_domains:
        print(f"\n❌ Registered ({len(registered_domains)}):")
        for domain in registered_domains:
            print(f"  • {domain}")
    
    if unknown_domains:
        print(f"\n⚠️  Unknown ({len(unknown_domains)}):")
        for domain in unknown_domains:
            print(f"  • {domain}")
    
    print("\n💡 Note: This is not 100% accurate. Always verify manually.")
    print("   Use Namecheap, GoDaddy, or whois.com for final confirmation.")

if __name__ == '__main__':
    main()