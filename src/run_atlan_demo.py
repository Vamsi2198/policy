#!/usr/bin/env python3
"""
Atlan Actions Engine - Demo Setup & Runner
==========================================

Quick setup script to configure and run Atlan Actions demos.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version}")
    return True

def check_environment():
    """Check API keys and environment setup"""
    print("\n🔧 ENVIRONMENT CHECK:")
    
    # Check AI API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY configured (Claude mode)")
        ai_mode = "Claude"
    elif openai_key:
        print("✅ OPENAI_API_KEY configured (OpenAI mode)")
        ai_mode = "OpenAI"
    else:
        print("⚠️  No AI API keys - using local fallback")
        ai_mode = "Local"
    
    # Check Atlan configuration
    atlan_url = os.getenv('ATLAN_BASE_URL', 'https://demo.atlan.com')
    atlan_token = os.getenv('ATLAN_API_TOKEN')
    
    if atlan_token:
        print(f"✅ ATLAN_API_TOKEN configured")
        print(f"🌐 Atlan URL: {atlan_url}")
        atlan_enabled = True
    else:
        print("⚠️  ATLAN_API_TOKEN not set - demo mode only")
        atlan_enabled = False
    
    return ai_mode, atlan_enabled

def setup_demo_data():
    """Setup demo database if needed"""
    print("\n📊 DEMO DATA SETUP:")
    
    # Check if we have database connection
    try:
        from control_pannel import ControlPlaneEngine
        engine = ControlPlaneEngine("config.yaml")
        if engine.connect_platform():
            print("✅ Database connection available")
            return True
        else:
            print("⚠️  Database connection failed - using mock data")
            return False
    except Exception as e:
        print(f"⚠️  Database setup error: {e}")
        return False

def run_environment_setup():
    """Guide user through environment setup"""
    print("\n" + "="*70)
    print("🚀 ATLAN ACTIONS ENGINE - DEMO SETUP")
    print("="*70)
    
    print("""
To get the most out of this demo, you can configure:

1. 🤖 AI API (for natural language processing):
   export ANTHROPIC_API_KEY="your_claude_key"
   OR
   export OPENAI_API_KEY="your_openai_key"

2. 🏷️  Atlan API (for catalog integration):
   export ATLAN_BASE_URL="https://your-tenant.atlan.com"
   export ATLAN_API_TOKEN="your_atlan_token"

3. 💾 Database (optional - will use demo data if not available):
   Configure config.yaml with your Snowflake/BigQuery credentials

Don't worry if you don't have these - the demo will work with fallbacks!
    """)
    
    response = input("\nDo you want to set up API keys now? (y/N): ").strip().lower()
    
    if response == 'y':
        print("\n🔧 API KEY SETUP:")
        
        # AI API setup
        ai_choice = input("Choose AI provider (1=Claude, 2=OpenAI, 3=Skip): ").strip()
        if ai_choice == '1':
            claude_key = input("Enter Anthropic API key: ").strip()
            if claude_key:
                os.environ['ANTHROPIC_API_KEY'] = claude_key
                print("✅ Claude API key set for this session")
        elif ai_choice == '2':
            openai_key = input("Enter OpenAI API key: ").strip()
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                print("✅ OpenAI API key set for this session")
        
        # Atlan API setup
        atlan_choice = input("\nSet up Atlan integration? (y/N): ").strip().lower()
        if atlan_choice == 'y':
            atlan_url = input("Enter Atlan URL (https://your-tenant.atlan.com): ").strip()
            atlan_token = input("Enter Atlan API token: ").strip()
            
            if atlan_url and atlan_token:
                os.environ['ATLAN_BASE_URL'] = atlan_url
                os.environ['ATLAN_API_TOKEN'] = atlan_token
                print("✅ Atlan API configured for this session")

def show_demo_menu():
    """Show interactive demo menu"""
    print("\n" + "="*70)
    print("🎯 ATLAN ACTIONS ENGINE - DEMO MENU")
    print("="*70)
    
    ai_mode, atlan_enabled = check_environment()
    
    print(f"""
🔧 CURRENT CONFIGURATION:
   🤖 AI Mode: {ai_mode}
   🏷️  Atlan Integration: {'✅ Enabled' if atlan_enabled else '❌ Demo Mode'}
   
🎭 AVAILABLE DEMOS:
   1. 🚀 Quick Demo (5 minutes)
      - Basic PII masking
      - Atlan sync demonstration
      
   2. 🎬 Executive Demo (15 minutes)
      - Full 4-scenario walkthrough
      - Business value presentation
      - Technical deep dive
      
   3. 🛠️  Interactive Mode
      - Direct commands to Atlan Actions Engine
      - Real-time natural language processing
      
   4. 🧪 Test Specific Feature
      - Multi-mode execution (Direct vs Airflow)
      - Autonomous discovery
      - Learning engine
      
   5. ⚙️  Environment Setup
      - Configure API keys
      - Test connections
      
   6. 📖 View Documentation
      - Architecture overview
      - API reference
      
   7. 🚪 Exit
    """)

def run_interactive_demo():
    """Run interactive Atlan Actions mode"""
    print("\n🛠️  INTERACTIVE ATLAN ACTIONS MODE")
    print("="*50)
    print("Type natural language governance commands.")
    print("Examples:")
    print("  - 'mask pii in customers table'")
    print("  - 'automatically discover and protect sensitive data'")
    print("  - 'generate airflow dag for email masking'")
    print("Type 'quit' to exit.\n")
    
    try:
        from atlan_ai_control_plane import AtlanActionsEngine
        
        # Initialize with current environment
        atlan_config = None
        if os.getenv('ATLAN_API_TOKEN'):
            atlan_config = {
                'base_url': os.getenv('ATLAN_BASE_URL', 'https://demo.atlan.com'),
                'api_token': os.getenv('ATLAN_API_TOKEN')
            }
        
        actions_engine = AtlanActionsEngine(
            execution_mode="direct",
            atlan_config=atlan_config
        )
        
        while True:
            user_input = input("🎯 Atlan Actions: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Exiting interactive mode...")
                break
            
            if not user_input:
                continue
            
            print(f"\n⚡ Processing: '{user_input}'")
            
            try:
                results = actions_engine.process_natural_language(user_input)
                
                if results.get('status') == 'success':
                    print(f"✅ SUCCESS in {results.get('total_time', 0):.2f}s")
                    
                    # Show key results
                    exec_result = results['phases'].get('execute', {})
                    atlan_status = exec_result.get('atlan_sync_status', {})
                    
                    if atlan_status.get('enabled'):
                        synced_count = len(atlan_status.get('synced_items', []))
                        print(f"🏷️  Atlan: Synced {synced_count} items")
                    
                    learn_result = results['phases'].get('learn', {})
                    for rec in learn_result.get('recommendations', [])[:2]:
                        print(f"💡 {rec}")
                else:
                    print(f"❌ {results.get('status', 'ERROR').upper()}: {results.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()  # Empty line for readability
            
    except ImportError as e:
        print(f"❌ Cannot start interactive mode: {e}")
        print("Make sure atlan_ai_control_plane.py is available")

def show_documentation():
    """Show architecture and usage documentation"""
    print("\n📖 ATLAN ACTIONS ENGINE - DOCUMENTATION")
    print("="*60)
    
    print("""
🏗️  ARCHITECTURE OVERVIEW:

   Data Sources → Atlan Catalog → ATLAN ACTIONS → Orchestration
                                      ↓
                               6-Phase Governance Loop:
                               OBSERVE → ANALYZE → PLAN 
                               → SIMULATE → EXECUTE → LEARN

🎯 CORE CAPABILITIES:

   1. Natural Language Processing
      - Convert governance commands to SQL
      - Intent recognition and entity extraction
      - Confidence scoring and validation

   2. 6-Phase Autonomous Loop
      - OBSERVE: Schema analysis and data sampling
      - ANALYZE: PII detection and impact assessment
      - PLAN: SQL generation and execution planning
      - SIMULATE: Impact preview and risk assessment
      - EXECUTE: Policy deployment with rollback
      - LEARN: Pattern discovery and recommendations

   3. Atlan Catalog Integration
      - Real-time classification sync
      - Governance lineage creation
      - Custom metadata storage

   4. Multi-Mode Execution
      - Direct: Immediate execution
      - Airflow: DAG generation for orchestration
      - Prefect: Flow generation (coming soon)

🚀 USAGE EXAMPLES:

   Basic Commands:
   - "mask pii in customers table"
   - "delete user data for GDPR compliance"
   - "discover sensitive data in all tables"

   Advanced Commands:
   - "automatically discover PII and apply intelligent masking"
   - "generate airflow dag for email address protection"
   - "analyze data classification patterns and recommend policies"

📊 PERFORMANCE:
   - Typical execution: 2-10 seconds
   - Database scan: 30-60 seconds (depending on size)
   - Atlan sync: 1-3 seconds per entity

🔧 CONFIGURATION:

   Environment Variables:
   - ANTHROPIC_API_KEY or OPENAI_API_KEY (for AI processing)
   - ATLAN_BASE_URL and ATLAN_API_TOKEN (for catalog sync)
   - Database credentials in config.yaml

   Execution Modes:
   - Direct: Immediate governance action
   - Airflow: Generate DAG for scheduled execution
   - Prefect: Generate flow for workflow orchestration
    """)
    
    input("\nPress ENTER to continue...")

def main():
    """Main demo runner"""
    if not check_python_version():
        return
    
    while True:
        show_demo_menu()
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            # Quick demo
            try:
                from atlan_actions_demo import run_quick_demo
                run_quick_demo()
            except ImportError:
                print("❌ Demo script not found")
        
        elif choice == '2':
            # Executive demo
            try:
                from atlan_actions_demo import run_executive_demo
                run_executive_demo()
            except ImportError:
                print("❌ Demo script not found")
        
        elif choice == '3':
            # Interactive mode
            run_interactive_demo()
        
        elif choice == '4':
            # Test specific features
            print("\n🧪 FEATURE TESTING:")
            print("1. Multi-mode execution")
            print("2. Autonomous discovery")
            print("3. Learning engine")
            
            feature = input("Select feature (1-3): ").strip()
            if feature in ['1', '2', '3']:
                print(f"Testing feature {feature}... (Not implemented in demo)")
            
        elif choice == '5':
            # Environment setup
            run_environment_setup()
        
        elif choice == '6':
            # Documentation
            show_documentation()
        
        elif choice == '7':
            # Exit
            print("\n👋 Thank you for exploring Atlan Actions Engine!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()