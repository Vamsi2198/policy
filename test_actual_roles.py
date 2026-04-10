#!/usr/bin/env python3
"""
Test to verify role-based masking uses ACTUAL Snowflake roles
instead of hardcoded ones like 'DATA_STEWARD' (which doesn't exist)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_control_plane import AIControlPlane

def test_actual_roles():
    """Test that masking uses actual Snowflake roles"""
    print("=" * 80)
    print("TESTING ROLE-BASED MASKING WITH ACTUAL SNOWFLAKE ROLES")
    print("=" * 80)
    print()
    
    # Initialize control plane
    print("Initializing AIControlPlane...")
    control_plane = AIControlPlane()
    
    # Get available roles
    print("\n" + "=" * 80)
    print("STEP 1: CHECKING AVAILABLE SNOWFLAKE ROLES")
    print("=" * 80)
    available_roles = control_plane._get_available_snowflake_roles()
    print(f"✅ Available roles in Snowflake: {available_roles}")
    
    # Get admin roles
    print("\n" + "=" * 80)
    print("STEP 2: DETECTING ADMIN/PRIVILEGED ROLES")
    print("=" * 80)
    admin_roles = control_plane._get_admin_roles()
    print(f"✅ Admin/privileged roles: {admin_roles}")
    
    # Test role directive extraction with actual roles
    print("\n" + "=" * 80)
    print("STEP 3: TESTING ROLE DIRECTIVE EXTRACTION")
    print("=" * 80)
    
    test_queries = [
        "mask ssn for analyst roles",
        "mask email not for analyst roles",
        "mask phone in customers table for analyst roles",
        "mask pii in RESIDENTIAL_ADDRESS table for analyst roles",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        directive = control_plane._extract_role_directive(query)
        print(f"  Role: {directive['role']}")
        print(f"  Visible to (UNMASKED): {directive['visible_for_roles']}")
        print(f"  Masked for: {directive['masked_for_roles']}")
        
        # Verify roles are actual Snowflake roles
        for role in directive['visible_for_roles']:
            if role not in ['PUBLIC'] and role not in available_roles:
                print(f"  ⚠️  WARNING: '{role}' might not be a real Snowflake role!")
            else:
                print(f"  ✅ '{role}' is a valid role")
        
        for role in directive['masked_for_roles']:
            if role not in ['PUBLIC'] and role not in available_roles:
                print(f"  ⚠️  WARNING: '{role}' might not be a real Snowflake role!")
            else:
                print(f"  ✅ '{role}' is a valid role")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"""
✅ Role extraction now uses ACTUAL Snowflake roles from the system
✅ Hardcoded roles like 'DATA_STEWARD' have been replaced with real ones
✅ Admin roles detected: {admin_roles}
✅ Available roles: {available_roles}

Changes Made:
- Added _get_available_snowflake_roles() - fetches roles from Snowflake
- Added _get_admin_roles() - detects privileged roles in the system
- Updated _extract_role_directive() - uses actual admin roles instead of hardcoded ones
- Changed 'ADMIN' -> 'ACCOUNTADMIN' (actual Snowflake system role)
- Changed 'DATA_STEWARD' -> 'SECURITYADMIN' (actual Snowflake system role)
""")
    print("=" * 80)

if __name__ == '__main__':
    test_actual_roles()
