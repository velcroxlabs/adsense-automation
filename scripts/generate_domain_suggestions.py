#!/usr/bin/env python3
"""
Generate domain name suggestions for AdSense Automation project.
Focuses on generic, memorable names that encompass all three niches.
"""

import itertools

# Word banks
primary_words = [
    'smart', 'easy', 'quick', 'simple', 'practical', 'essential',
    'ultimate', 'complete', 'comprehensive', 'expert', 'pro',
    'modern', 'digital', 'online', 'virtual', 'auto', 'auto',
    'instant', 'rapid', 'fast', 'efficient', 'effective'
]

secondary_words = [
    'guide', 'hub', 'central', 'nexus', 'matrix', 'network',
    'portal', 'gateway', 'resource', 'library', 'archive',
    'vault', 'repository', 'collection', 'compendium', 'manual',
    'handbook', 'playbook', 'blueprint', 'framework', 'system',
    'platform', 'engine', 'toolkit', 'suite', 'package'
]

niche_words = [
    'life', 'living', 'lifestyle', 'home', 'finance', 'money',
    'wealth', 'health', 'wellness', 'fitness', 'improvement',
    'growth', 'development', 'skills', 'knowledge', 'wisdom',
    'insights', 'solutions', 'strategies', 'tips', 'tricks',
    'hacks', 'advice', 'recommendations', 'reviews'
]

# Single word domains (strong brands)
single_words = [
    'nexus', 'matrix', 'hub', 'central', 'guide', 'manual',
    'handbook', 'blueprint', 'framework', 'platform', 'engine',
    'toolkit', 'compass', 'oracle', 'forge', 'lab', 'works',
    'factory', 'mill', 'foundry', 'studio', 'academy', 'institute'
]

def generate_combinations():
    """Generate domain name combinations."""
    suggestions = []
    
    # Primary + Secondary (e.g., SmartGuide, EasyHub)
    for p in primary_words[:15]:
        for s in secondary_words[:15]:
            suggestions.append(f"{p}{s}")
    
    # Niche + Secondary (e.g., LifeHub, FinanceGuide)
    for n in niche_words[:15]:
        for s in secondary_words[:10]:
            suggestions.append(f"{n}{s}")
    
    # Primary + Niche (e.g., SmartLife, EasyFinance)
    for p in primary_words[:10]:
        for n in niche_words[:10]:
            suggestions.append(f"{p}{n}")
    
    # Three-word combinations (limit)
    three_word = [
        'SmartLifeGuide', 'EasyFinanceHub', 'QuickHealthCentral',
        'PracticalHomeHub', 'EssentialWealthGuide', 'UltimateWellnessHub',
        'CompleteImprovementGuide', 'ExpertSkillsHub', 'ModernLifestyleGuide',
        'DigitalSolutionsHub', 'OnlineAdviceCentral', 'VirtualTipsHub',
        'AutoGuideCentral', 'InstantAdviceHub', 'RapidSolutionsGuide'
    ]
    suggestions.extend(three_word)
    
    # Single word + .com
    suggestions.extend(single_words)
    
    # Add "The" prefix variations
    the_prefix = [f"The{word}" for word in single_words[:10]]
    suggestions.extend(the_prefix)
    
    # Remove duplicates and sort
    suggestions = list(set(suggestions))
    suggestions.sort(key=lambda x: (len(x), x))
    
    return suggestions

def main():
    print("🔍 Generating domain name suggestions...")
    print("="*60)
    
    domains = generate_combinations()
    
    print(f"Generated {len(domains)} domain ideas")
    print("\nTop 50 suggestions (add .com):")
    print("-"*40)
    
    for i, domain in enumerate(domains[:50], 1):
        print(f"{i:2d}. {domain.lower()}.com")
    
    print("\n💡 Tips for choosing:")
    print("1. Memorable & easy to spell")
    print("2. 6-14 characters ideal")
    print("3. Avoid numbers/hyphens")
    print("4. Consider .net/.org if .com taken")
    print("5. Check trademark availability")
    
    # Save to file
    with open('domain_ideas.txt', 'w') as f:
        f.write("Domain Ideas for AdSense Automation\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total ideas: {len(domains)}\n\n")
        
        f.write("All suggestions (.com):\n")
        for domain in domains:
            f.write(f"- {domain.lower()}.com\n")
        
        f.write("\n\nTop recommendations:\n")
        f.write("1. nexus.com (if available, unlikely)\n")
        f.write("2. guidehub.com\n")
        f.write("3. smartcentral.com\n")
        f.write("4. lifematrix.com\n")
        f.write("5. practicalhub.com\n")
        f.write("6. expertguide.com\n")
        f.write("7. onlinemanual.com\n")
        f.write("8. digitalblueprint.com\n")
        f.write("9. autoguide.com\n")
        f.write("10. solutionshub.com\n")
    
    print(f"\n📄 Full list saved to 'domain_ideas.txt'")
    print("\n⚠️  Remember: Most .com domains are registered.")
    print("   Be prepared with .net/.org alternatives.")

if __name__ == '__main__':
    main()