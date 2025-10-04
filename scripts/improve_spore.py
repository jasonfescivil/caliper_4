#!/usr/bin/env python
"""
Improve spore responses in existing retrieval context files.
This script re-processes context files to generate better spore explanations.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

def generate_better_spore(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a more detailed and useful spore analysis."""
    
    question = data.get("question", "")
    nodes = (data.get("retrieval") or {}).get("nodes", [])
    indexes = data.get("indexes", [])
    
    if not nodes:
        return {
            "summary": "No nodes retrieved for analysis.",
            "rationale_bullets": [],
            "confidence": 0.0
        }
    
    # Analyze what's actually in the retrieved content
    regulations_found = set()
    standards_found = set()
    topics_covered = set()
    jurisdictions = set()
    
    for node in nodes[:20]:  # Analyze top 20 nodes
        md = node.get("metadata", {})
        text = node.get("text", "")
        
        # Extract regulation references
        import re
        
        # Federal regulations
        cfr_matches = re.findall(r'\b(?:40|33)\s+CFR\s+[\d.]+', text, re.IGNORECASE)
        regulations_found.update(cfr_matches)
        
        # Washington state codes
        wac_matches = re.findall(r'\bWAC\s+[\d-]+', text, re.IGNORECASE)
        regulations_found.update(wac_matches)
        
        rcw_matches = re.findall(r'\bRCW\s+[\d.]+', text, re.IGNORECASE)
        regulations_found.update(rcw_matches)
        
        # Standards
        if 'AASHTO' in text.upper():
            standards_found.add('AASHTO')
        if 'WEF' in text.upper():
            standards_found.add('WEF')
        if 'ASCE' in text.upper():
            standards_found.add('ASCE')
        if 'AWWA' in text.upper():
            standards_found.add('AWWA')
        if 'TEN STATE' in text.upper() or 'TEN-STATE' in text.upper():
            standards_found.add('Ten States Standards')
            
        # Extract topics
        if 'effluent' in text.lower():
            topics_covered.add('effluent limits')
        if 'WWTP' in text.upper() or 'wastewater treatment' in text.lower():
            topics_covered.add('WWTP requirements')
        if 'bridge' in text.lower() and 'foundation' in text.lower():
            topics_covered.add('bridge foundations')
        if 'population' in text.lower() and 'projection' in text.lower():
            topics_covered.add('population projections')
        if 'flow' in text.lower() and ('design' in text.lower() or 'peak' in text.lower()):
            topics_covered.add('flow calculations')
        if 'permit' in text.lower():
            topics_covered.add('permitting')
        if 'monitoring' in text.lower():
            topics_covered.add('monitoring requirements')
            
        # Extract jurisdiction
        jurisdiction = md.get("jurisdiction", "")
        if jurisdiction:
            jurisdictions.add(jurisdiction)
    
    # Build detailed rationale bullets
    rationale_bullets = []
    
    if regulations_found:
        reg_list = list(regulations_found)[:5]  # Top 5
        rationale_bullets.append(f"Retrieved content covers {len(regulations_found)} regulatory sections including {', '.join(reg_list)}")
    
    if standards_found:
        rationale_bullets.append(f"Includes technical standards from {', '.join(sorted(standards_found))}")
    
    if topics_covered:
        topic_list = list(topics_covered)[:4]
        rationale_bullets.append(f"Addresses {len(topics_covered)} key topics: {', '.join(topic_list)}")
    
    # Analyze coverage across indexes
    index_coverage = {}
    for node in nodes:
        idx = node.get("metadata", {}).get("index", "unknown")
        index_coverage[idx] = index_coverage.get(idx, 0) + 1
    
    if len(index_coverage) > 1:
        coverage_desc = ", ".join([f"{k}: {v}" for k, v in sorted(index_coverage.items())[:3]])
        rationale_bullets.append(f"Cross-references {len(index_coverage)} indexes with distribution: {coverage_desc}")
    
    # Analyze relevance to question
    question_lower = question.lower()
    if "crosswalk" in question_lower:
        rationale_bullets.append("Provides comparative regulatory framework suitable for crosswalk analysis")
    if "WWTP" in question.upper() or "wastewater" in question_lower:
        wwtp_count = sum(1 for n in nodes if "WWTP" in n.get("text", "").upper() or "wastewater" in n.get("text", "").lower())
        if wwtp_count > 0:
            rationale_bullets.append(f"Contains {wwtp_count} nodes specifically addressing wastewater treatment requirements")
    if "bridge" in question_lower:
        bridge_count = sum(1 for n in nodes if "bridge" in n.get("text", "").lower())
        if bridge_count > 0:
            rationale_bullets.append(f"Found {bridge_count} nodes with bridge-specific engineering guidance")
    
    # Calculate confidence based on actual coverage
    confidence = 0.5  # Base confidence
    
    if regulations_found:
        confidence += 0.2
    if standards_found:
        confidence += 0.15
    if len(topics_covered) >= 3:
        confidence += 0.1
    if len(index_coverage) > 1:
        confidence += 0.05
    
    confidence = min(0.95, confidence)  # Cap at 0.95
    
    # Generate summary
    if regulations_found and standards_found:
        summary = f"Retrieved {len(nodes)} nodes covering {len(regulations_found)} regulations and {len(standards_found)} design standards relevant to {question[:100]}. Strong regulatory and technical coverage achieved."
    elif regulations_found:
        summary = f"Retrieved {len(nodes)} nodes with {len(regulations_found)} regulatory citations relevant to {question[:100]}. Good regulatory coverage, limited design standards."
    elif standards_found:
        summary = f"Retrieved {len(nodes)} nodes referencing {len(standards_found)} technical standards for {question[:100]}. Technical guidance available, regulatory coverage may need expansion."
    else:
        summary = f"Retrieved {len(nodes)} nodes addressing {len(topics_covered)} topics related to {question[:100]}. Consider refining search parameters for better regulatory/standards coverage."
    
    return {
        "summary": summary,
        "rationale_bullets": rationale_bullets[:5],  # Keep top 5 most relevant
        "confidence": round(confidence, 2),
        "analysis_metadata": {
            "regulations_found": list(regulations_found)[:10],
            "standards_found": list(standards_found),
            "topics_covered": list(topics_covered),
            "jurisdictions": list(jurisdictions)
        }
    }

def improve_spore_in_file(filepath: Path) -> None:
    """Improve the spore in a single context file."""
    
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if this is a retrieval context file
    if data.get("type") not in ["retrieval_session", "enhanced_retrieval"]:
        print(f"  Skipping - not a retrieval context file (type: {data.get('type')})")
        return
    
    # Generate better spore
    better_spore = generate_better_spore(data)
    
    # Update the spore in the data structure
    if "retrieval" in data:
        data["retrieval"]["spore"] = better_spore
    else:
        data["spore"] = better_spore
    
    # For enhanced files, update the rewritten spore too
    if data.get("type") == "enhanced_retrieval" and "spore" in data:
        data["spore"]["rewritten"] = better_spore
    
    # Save the improved file
    backup_path = filepath.with_suffix('.bak.json')
    filepath.rename(backup_path)
    print(f"  Backed up original to: {backup_path}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  Updated with better spore analysis")
    print(f"  Confidence: {better_spore['confidence']}")
    print(f"  Bullets: {len(better_spore['rationale_bullets'])}")
    print()

def main():
    """Process context files to improve spore responses."""
    
    if len(sys.argv) > 1:
        # Process specific files
        for arg in sys.argv[1:]:
            filepath = Path(arg)
            if filepath.exists() and filepath.suffix == '.json':
                improve_spore_in_file(filepath)
            else:
                print(f"Skipping {arg} - not a valid JSON file")
    else:
        # Process all context files in data_v2/context
        context_dir = Path("data_v2/context")
        if not context_dir.exists():
            print(f"Context directory not found: {context_dir}")
            return
        
        json_files = list(context_dir.glob("*.json"))
        print(f"Found {len(json_files)} JSON files in {context_dir}")
        print()
        
        for filepath in json_files:
            try:
                improve_spore_in_file(filepath)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue

if __name__ == "__main__":
    main()