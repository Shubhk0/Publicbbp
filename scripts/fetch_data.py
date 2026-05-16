#!/usr/bin/env python3
import json
import urllib.request
import os

def fetch_and_merge():
    merged_programs = {}

    # 1. ProjectDiscovery Data
    print("Fetching ProjectDiscovery data...")
    try:
        req = urllib.request.Request('https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/main/dist/data.json')
        with urllib.request.urlopen(req) as response:
            pd_data = json.loads(response.read().decode())
            for p in pd_data.get('programs', []):
                name = p.get('name')
                if not name: continue
                merged_programs[name.lower()] = {
                    'name': name,
                    'url': p.get('url', ''),
                    'bounty': p.get('bounty', False),
                    'swag': p.get('swag', False),
                    'domains': p.get('domains', []),
                    'source': 'ProjectDiscovery'
                }
    except Exception as e:
        print("Error fetching ProjectDiscovery data:", e)

    # 2. Disclose.io Data
    print("Fetching Disclose.io data...")
    try:
        req = urllib.request.Request('https://raw.githubusercontent.com/disclose/diodb/master/program-list.json')
        with urllib.request.urlopen(req) as response:
            dio_data = json.loads(response.read().decode())
            for p in dio_data:
                name = p.get('program_name')
                if not name: continue
                key = name.lower()
                if key in merged_programs:
                    if not merged_programs[key]['url']:
                        merged_programs[key]['url'] = p.get('policy_url', '')
                    merged_programs[key]['bounty'] = merged_programs[key]['bounty'] or (str(p.get('offers_bounty', '')).lower() == 'yes')
                    merged_programs[key]['swag'] = merged_programs[key]['swag'] or (p.get('offers_swag') == True)
                    if 'Disclose.io' not in merged_programs[key]['source']:
                        merged_programs[key]['source'] += ', Disclose.io'
                else:
                    merged_programs[key] = {
                        'name': name,
                        'url': p.get('policy_url', ''),
                        'bounty': str(p.get('offers_bounty', '')).lower() == 'yes',
                        'swag': p.get('offers_swag') == True,
                        'domains': [],
                        'source': 'Disclose.io'
                    }
    except Exception as e:
        print("Error fetching Disclose.io data:", e)

    # Save merged data
    final_list = list(merged_programs.values())
    final_list.sort(key=lambda x: x['name'].lower())

    os.makedirs('data', exist_ok=True)
    with open('data/programs.json', 'w', encoding='utf-8') as f:
        json.dump({'programs': final_list}, f, indent=2)

    print(f"Successfully fetched and merged {len(final_list)} programs.")

if __name__ == "__main__":
    fetch_and_merge()
