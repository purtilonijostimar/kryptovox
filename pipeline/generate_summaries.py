#!/usr/bin/env python3
"""
Generate a 2-3 sentence executive summary for each account using Groq.
Saves summaries into docs/dashboard.json under the 'summary' key.
Skips accounts that already have a summary.
"""
import json, os, sys, time
from groq import Groq

DASHBOARD = os.path.join(os.path.dirname(__file__), '..', 'docs', 'dashboard.json')
GROQ_KEY = os.environ.get('GROQ_API_KEY')
if not GROQ_KEY:
    raise RuntimeError('Set GROQ_API_KEY env var')

client = Groq(api_key=GROQ_KEY)

def first(val):
    if isinstance(val, list):
        return next((v for v in val if v), None)
    return val

def build_prompt(a):
    loc = ', '.join(filter(None, [a.get('location_state_region'), a.get('location_country')]))
    terrain = first(a.get('terrain_type')) or 'unknown terrain'
    profession = a.get('profession_category') or 'unknown profession'
    age = a.get('approximate_age')
    distance = first(a.get('distance_metres'))
    delay = a.get('disclosure_delay_years')
    wcs = a.get('WCS_raw', 0)
    band = a.get('WCS_band', '')
    height = first(a.get('height_estimate_ft'))
    eyes_glow = first(a.get('eyes_glow')) if isinstance(a.get('eyes_glow'), list) else a.get('eyes_glow')
    smell = first(a.get('smell_description')) or (first(a.get('smell_description_quote')) if isinstance(a.get('smell_description_quote'), list) else a.get('smell_description_quote'))
    face = first(a.get('face_type')) if isinstance(a.get('face_type'), list) else a.get('face_type')
    departure = first(a.get('departure_type')) if isinstance(a.get('departure_type'), list) else a.get('departure_type')
    narrator = a.get('narrator_profile')
    life_change = a.get('post_encounter_life_change')
    paralysis = a.get('paralysis_or_freeze')
    minimisation = bool(a.get('minimisation_phrases'))

    # Pull one strong evidence quote from IC or SS
    quote = None
    for dim in ['IC', 'SS', 'EA']:
        q = ((a.get(dim) or {}).get('evidence_quotes') or [])
        if q:
            quote = q[0]
            break

    parts = [
        f"Witness: {profession}, age {age}" if age else f"Witness: {profession}",
        f"Location: {loc}" if loc else None,
        f"Terrain: {terrain}",
        f"Distance at closest: {distance}" if distance else None,
        f"Estimated height: {height} ft" if height else None,
        f"Face described as: {face}" if face else None,
        f"Eyes self-illuminated: yes" if eyes_glow else None,
        f"Smell described: {smell}" if smell else None,
        f"Departure: {departure}" if departure else None,
        f"Disclosure delay: {delay} years" if delay else None,
        f"Post-encounter life change: yes" if life_change else None,
        f"Paralysis/freeze response: yes" if paralysis else None,
        f"Minimisation phrases present: yes" if minimisation else None,
        f"Narrator profile: {narrator}" if narrator else None,
        f"WCS score: {wcs:.1f} ({band})",
        f'Key quote: "{quote}"' if quote else None,
    ]
    data_block = '\n'.join(p for p in parts if p)

    return f"""You are writing for an academic research platform studying persistent unusual descriptors in witness testimony (Kryptovox). Write a 2-3 sentence executive summary of this specific witness account. Tone: precise, measured, academic but readable. Do not assert the creature exists. Do not use sensationalist language. Focus on what the witness reported and what makes this account notable from a credibility/pattern standpoint. Write in third person. No bullet points. No headers. Plain prose only.

Account data:
{data_block}

Write the executive summary now:"""

def main():
    with open(DASHBOARD) as f:
        data = json.load(f)

    accounts = data['accounts']
    todo = [a for a in accounts if not a.get('summary')]
    print(f"{len(todo)} accounts need summaries ({len(accounts) - len(todo)} already done)")

    for i, a in enumerate(todo):
        title = a.get('display_title') or a.get('episode_title') or a.get('video_id')
        sys.stdout.write(f"  [{i+1}/{len(todo)}] {title[:60]}... ")
        sys.stdout.flush()
        try:
            prompt = build_prompt(a)
            resp = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.4,
                max_tokens=180,
            )
            summary = resp.choices[0].message.content.strip()
            a['summary'] = summary
            print(f"✓ ({len(summary)} chars)")
        except Exception as e:
            print(f"ERROR: {e}")
            a['summary'] = ''
        
        # Save after every 10 to avoid losing progress
        if (i + 1) % 10 == 0:
            with open(DASHBOARD, 'w') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            print(f"  [saved at {i+1}]")
        
        time.sleep(0.3)  # stay well within rate limits

    with open(DASHBOARD, 'w') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f"\nDone. {len(todo)} summaries written.")

if __name__ == '__main__':
    main()
