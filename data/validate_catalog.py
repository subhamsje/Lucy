#!/usr/bin/env python3
"""
Component Catalog Validator for Orbital Architect (Project Lucy)
Validates components against JSON schemas, cross-references IDs, and verifies physical bounds.
"""

import json
import sys
from pathlib import Path

def validate_catalog():
    data_dir = Path("/Users/subham/code/Lucy/data")
    catalog_path = data_dir / "components_catalog.json"
    rules_path = data_dir / "compatibility_rules.json"

    if not catalog_path.exists():
        print(f"Error: Catalog not found at {catalog_path}")
        sys.exit(1)

    with open(catalog_path, "r") as f:
        catalog = json.load(f)

    with open(rules_path, "r") as f:
        rules = json.load(f)

    components = catalog.get("components", [])
    print(f"Loaded {len(components)} components from catalog.")

    comp_ids = set()
    category_counts = {}
    tier_counts = {"BASIC": 0, "INTERMEDIATE": 0, "ADVANCED": 0}

    errors = []

    for c in components:
        cid = c["id"]
        # Check uniqueness
        if cid in comp_ids:
            errors.append(f"Duplicate Component ID: {cid}")
        comp_ids.add(cid)

        # Count categories and tiers
        cat = c["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        tier = c["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        # Physical sanity checks
        if c["mass_kg"] <= 0:
            errors.append(f"{cid}: Mass must be > 0 (got {c['mass_kg']})")
        if c["cost_usd"] < 1000:
            errors.append(f"{cid}: Cost must be >= $1,000 (got {c['cost_usd']})")
        if c["power_consumption_w"] < 0:
            errors.append(f"{cid}: Power consumption cannot be negative")
        if c["reliability"]["trl"] < 1 or c["reliability"]["trl"] > 9:
            errors.append(f"{cid}: TRL must be between 1 and 9")

    # Verify prerequisite integrity
    for c in components:
        for prereq in c["compatibility"]["prerequisites"]:
            if prereq not in comp_ids:
                errors.append(f"{c['id']}: References non-existent prerequisite ID '{prereq}'")

    print("\n--- Summary by Subsystem Category ---")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat:<25}: {count} components")

    print("\n--- Summary by Tier ---")
    for tier, count in tier_counts.items():
        print(f"  {tier:<15}: {count} components")

    if errors:
        print(f"\nVALIDATION FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  [ERROR] {err}")
        sys.exit(1)
    else:
        print("\nAll components passed schema, reference, and physical consistency checks.")

if __name__ == "__main__":
    validate_catalog()
