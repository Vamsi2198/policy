#!/usr/bin/env python3
"""
Atlan Actions Engine - Executive Demo Script
============================================

This demo showcases the Atlan Actions Engine as the governance automation layer
between Atlan catalog and orchestration systems.

Demo Flow:
1. Setup & Initialization
2. Basic PII Masking with Atlan Sync
3. Autonomous Discovery & Classification
4. Multi-Mode Execution (Direct vs Airflow)
5. Governance Recommendations & Learning
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from atlan_ai_control_plane import AtlanActionsEngine, ExecutionMode
from decimal import Decimal

class DemoPresenter:
    """Executive demo presenter for Atlan Actions Engine"""
    
    def __init__(self):
        self.demo_start_time = None
        self.demo_results = []
        
    def print_header(self, title: str, subtitle: str = ""):
        """Print formatted demo section header"""
        print("\n" + "="*90)
        print(f"🎯 {title}")
        if subtitle:
            print(f"   {subtitle}")
        print("="*90)
    
    def print_step(self, step_num: int, total_steps: int, description: str):
        """Print demo step with progress"""
        print(f"\n🚀 STEP {step_num}/{total_steps}: {description}")
        print("-" * 70)
    
    def pause_for_effect(self, message: str = "Press ENTER to continue", duration: float = 1.0):
        """Pause for dramatic effect in presentation"""
        time.sleep(duration)
        input(f"\n⏸️  {message}...")
    
    def show_results_summary(self, results: Dict[str, Any], title: str = "Results"):
        """Display formatted results summary"""
        print(f"\n📊 {title.upper()}")
        print("-" * 50)
        
        if results.get('status') == 'success':
            print(f"✅ Status: SUCCESS")
            print(f"⏱️  Total Time: {results.get('total_time', 0):.2f}s")
            print(f"🎯 Intent: {results['phases']['observe']['intent']}")
            print(f"📈 Confidence: {results['phases']['observe']['confidence']:.1%}")
            
            # Show execution details
            exec_result = results['phases'].get('execute', {})
            print(f"💾 SQL Commands: {len(exec_result.get('commands_executed', []))}")
            print(f"📋 Rows Affected: {exec_result.get('rows_affected', 0):,}")
            
            # Highlight Atlan integration
            atlan_status = exec_result.get('atlan_sync_status', {})
            if atlan_status.get('enabled'):
                synced_count = len(atlan_status.get('synced_items', []))
                print(f"🏷️  Atlan Sync: ✅ Tagged {synced_count} items in catalog")
                
                for item in atlan_status.get('synced_items', [])[:3]:
                    if item['type'] == 'classification':
                        print(f"   📌 {item['entity']} → {', '.join(item['pii_types'])}")
                    elif item['type'] == 'lineage_process':
                        print(f"   🔗 Process: {item['process_name']}")
            else:
                print(f"🏷️  Atlan Sync: ⚠️ Not configured (demo mode)")
            
            # Show learning results
            learn_result = results['phases'].get('learn', {})
            if learn_result:
                print(f"\n🎓 LEARNING & RECOMMENDATIONS:")
                print(f"   ✅ Verification: {'PASSED' if learn_result.get('verification_status') else 'PENDING'}")
                print(f"   🔍 Patterns Found: {len(learn_result.get('discovered_patterns', []))}")
                
                for rec in learn_result.get('recommendations', [])[:3]:
                    print(f"   💡 {rec}")
        else:
            print(f"❌ Status: {results.get('status', 'UNKNOWN').upper()}")
            if results.get('error'):
                print(f"🔥 Error: {results['error']}")
    
    def demo_setup_and_intro(self):
        """Demo introduction and setup"""
        self.print_header(
            "ATLAN ACTIONS ENGINE - EXECUTIVE DEMO", 
            "The Governance Automation Layer Between Catalog and Orchestration"
        )
        
        print("""
🎯 WHAT IS ATLAN ACTIONS?
   Atlan Actions sits between your data catalog and orchestration systems,
   providing intelligent governance automation through natural language.

🏗️  ARCHITECTURE POSITION:
   Data Sources → Atlan Catalog → ATLAN ACTIONS → Orchestration (Airflow/Prefect)

🚀 KEY CAPABILITIES:
   ✅ Natural language governance commands
   ✅ 6-phase autonomous governance loop (OBSERVE → ANALYZE → PLAN → SIMULATE → EXECUTE → LEARN)
   ✅ Real-time Atlan catalog synchronization
   ✅ Multi-mode execution (Direct, Airflow DAG, Prefect Flow)
   ✅ PII discovery and intelligent masking
   ✅ Governance recommendations and pattern learning

🎭 DEMO SCENARIOS:
   1. Basic PII masking with catalog sync
   2. Autonomous discovery across entire database
   3. Multi-mode execution demonstration
   4. Learning and recommendations engine
        """)
        
        # Check environment setup
        print(f"\n🔧 ENVIRONMENT SETUP:")
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        atlan_token = os.getenv('ATLAN_API_TOKEN')
        
        if anthropic_key:
            print(f"   ✅ Claude API: Configured")
            nl_mode = "Claude"
        elif openai_key:
            print(f"   ✅ OpenAI API: Configured")
            nl_mode = "OpenAI"
        else:
            print(f"   ⚠️  AI APIs: Using local fallback")
            nl_mode = "Local"
        
        if atlan_token:
            print(f"   ✅ Atlan API: Configured")
        else:
            print(f"   ⚠️  Atlan API: Demo mode (no real sync)")
        
        print(f"   🎯 NL Processing Mode: {nl_mode}")
        
        self.pause_for_effect("Ready to start Atlan Actions demo")
        
        return nl_mode, bool(atlan_token)
    
    def demo_basic_pii_masking(self, actions_engine: AtlanActionsEngine):
        """Demo 1: Basic PII masking with Atlan sync"""
        self.print_step(1, 4, "Basic PII Masking with Atlan Catalog Sync")
        
        print("""
🎯 SCENARIO: Customer service team needs to mask PII in customer table
   • Natural language command: "mask pii in customers table"
   • Expected: Automatic PII detection and masking policy creation
   • Atlan Integration: Tag classified columns in catalog
        """)
        
        self.pause_for_effect("Execute PII masking command")
        
        query = "mask pii in customers table"
        print(f"\n💬 Command: '{query}'")
        
        start_time = time.time()
        results = actions_engine.process_natural_language(query)
        execution_time = time.time() - start_time
        
        self.show_results_summary(results, "PII Masking Results")
        
        print(f"\n🎯 KEY HIGHLIGHTS:")
        print(f"   ⚡ Speed: {execution_time:.2f}s end-to-end")
        print(f"   🧠 AI-powered entity recognition")
        print(f"   🏷️  Real-time catalog synchronization")
        print(f"   🔒 Production-ready masking policies")
        
        self.demo_results.append({
            'scenario': 'Basic PII Masking',
            'query': query,
            'time': execution_time,
            'success': results.get('status') == 'success'
        })
        
        return results
    
    def demo_autonomous_discovery(self, actions_engine: AtlanActionsEngine):
        """Demo 2: Autonomous PII discovery and classification"""
        self.print_step(2, 4, "Autonomous PII Discovery & Intelligent Classification")
        
        print("""
🎯 SCENARIO: Data governance team wants comprehensive PII audit
   • Natural language command: "automatically discover PII and apply intelligent masking"
   • Expected: Full database scan, ML-powered classification, batch policy creation
   • Atlan Integration: Comprehensive catalog tagging and lineage creation
        """)
        
        self.pause_for_effect("Execute autonomous discovery")
        
        query = "automatically discover PII and apply intelligent masking"
        print(f"\n💬 Command: '{query}'")
        
        start_time = time.time()
        results = actions_engine.process_natural_language(query)
        execution_time = time.time() - start_time
        
        self.show_results_summary(results, "Autonomous Discovery Results")
        
        # Show detailed discovery insights
        if results.get('status') == 'success':
            analyze_result = results['phases'].get('analyze', {})
            pii_findings = analyze_result.get('pii_findings', [])
            
            print(f"\n🔍 DISCOVERY INSIGHTS:")
            print(f"   📊 Tables Scanned: {len(set(f['table'] for f in pii_findings))}")
            print(f"   🏷️  PII Columns Found: {len(pii_findings)}")
            print(f"   🎯 ML Confidence: {analyze_result.get('ml_confidence', 0):.1%}")
            
            # Show PII type distribution
            pii_types = {}
            for finding in pii_findings:
                for pii_type in finding['pii_types']:
                    pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
            
            print(f"   📈 PII Distribution:")
            for pii_type, count in pii_types.items():
                print(f"      {pii_type}: {count} columns")
        
        print(f"\n🎯 KEY HIGHLIGHTS:")
        print(f"   🤖 Fully autonomous operation")
        print(f"   📊 Comprehensive database coverage")
        print(f"   🧠 ML-powered PII classification")
        print(f"   🏗️  Scalable to enterprise databases")
        
        self.demo_results.append({
            'scenario': 'Autonomous Discovery',
            'query': query,
            'time': execution_time,
            'success': results.get('status') == 'success'
        })
        
        return results
    
    def demo_multi_mode_execution(self, actions_engine: AtlanActionsEngine):
        """Demo 3: Multi-mode execution (Direct vs Airflow)"""
        self.print_step(3, 4, "Multi-Mode Execution: Direct vs Orchestration")
        
        print("""
🎯 SCENARIO: DevOps team needs governance workflows in Airflow
   • Mode 1: Direct execution (immediate)
   • Mode 2: Airflow DAG generation (orchestrated)
   • Expected: Same governance logic, different execution models
        """)
        
        self.pause_for_effect("Compare execution modes")
        
        query = "mask email addresses in users table"
        
        # Direct mode
        print(f"\n🚀 DIRECT MODE EXECUTION:")
        print(f"💬 Command: '{query}'")
        
        direct_engine = AtlanActionsEngine(execution_mode="direct")
        start_time = time.time()
        direct_results = direct_engine.process_natural_language(query)
        direct_time = time.time() - start_time
        
        print(f"   ⚡ Execution: {direct_time:.2f}s")
        print(f"   🎯 Mode: Immediate execution")
        
        # Airflow mode
        print(f"\n🛠️  AIRFLOW MODE EXECUTION:")
        print(f"💬 Command: '{query}'")
        
        airflow_engine = AtlanActionsEngine(execution_mode="airflow")
        start_time = time.time()
        airflow_results = airflow_engine.process_natural_language(query)
        airflow_time = time.time() - start_time
        
        print(f"   ⚡ Generation: {airflow_time:.2f}s")
        print(f"   🎯 Mode: DAG code generation")
        
        # Show comparison
        print(f"\n📊 MODE COMPARISON:")
        print(f"   🚀 Direct: Immediate governance action")
        print(f"   🛠️  Airflow: Scheduled/orchestrated governance")
        print(f"   🎯 Same intelligence, different execution")
        
        # Show sample DAG if generated
        exec_result = airflow_results['phases'].get('execute', {})
        if exec_result.get('success'):
            commands = exec_result.get('commands_executed', [])
            if commands and 'DAG' in commands[0]:
                print(f"\n🛠️  GENERATED AIRFLOW DAG:")
                print(f"   📋 Tasks: SQL execution + Atlan sync")
                print(f"   🔗 Dependencies: Sequential with rollback")
                print(f"   ⏰ Schedule: On-demand governance")
        
        self.demo_results.append({
            'scenario': 'Multi-Mode Execution',
            'query': query,
            'time': direct_time,
            'success': direct_results.get('status') == 'success'
        })
        
        return direct_results, airflow_results
    
    def demo_learning_recommendations(self, actions_engine: AtlanActionsEngine):
        """Demo 4: Learning engine and governance recommendations"""
        self.print_step(4, 4, "Learning Engine & Governance Recommendations")
        
        print("""
🎯 SCENARIO: Continuous governance improvement through ML learning
   • Pattern discovery across governance actions
   • Intelligent recommendations for similar scenarios
   • Confidence feedback loops for model improvement
        """)
        
        self.pause_for_effect("Show learning capabilities")
        
        query = "discover sensitive data patterns for recommendation engine"
        print(f"\n💬 Command: '{query}'")
        
        start_time = time.time()
        results = actions_engine.process_natural_language(query)
        execution_time = time.time() - start_time
        
        # Enhanced learning insights
        if results.get('status') == 'success':
            learn_result = results['phases'].get('learn', {})
            
            print(f"\n🎓 LEARNING ENGINE INSIGHTS:")
            print(f"   🔍 Pattern Discovery: {len(learn_result.get('discovered_patterns', []))} patterns")
            print(f"   📈 Confidence Feedback: {learn_result.get('confidence_feedback', 0):.1%}")
            print(f"   ✅ Verification Status: {'PASSED' if learn_result.get('verification_status') else 'PENDING'}")
            
            print(f"\n🚀 GOVERNANCE RECOMMENDATIONS:")
            recommendations = learn_result.get('recommendations', [])
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec}")
            
            # Show performance metrics
            perf_impact = learn_result.get('performance_impact', {})
            if perf_impact:
                print(f"\n📊 PERFORMANCE IMPACT:")
                for metric, value in perf_impact.items():
                    print(f"   📈 {metric}: {value}")
        
        print(f"\n🎯 KEY HIGHLIGHTS:")
        print(f"   🧠 Continuous learning from governance actions")
        print(f"   🔄 Pattern recognition for similar scenarios")
        print(f"   📈 Model improvement through feedback loops")
        print(f"   🎯 Proactive governance recommendations")
        
        self.demo_results.append({
            'scenario': 'Learning & Recommendations',
            'query': query,
            'time': execution_time,
            'success': results.get('status') == 'success'
        })
        
        return results
    
    def demo_summary_and_conclusion(self):
        """Final demo summary and business value"""
        self.print_header("ATLAN ACTIONS ENGINE - DEMO SUMMARY & BUSINESS VALUE")
        
        total_scenarios = len(self.demo_results)
        successful_scenarios = sum(1 for r in self.demo_results if r['success'])
        total_demo_time = time.time() - self.demo_start_time
        avg_execution_time = sum(r['time'] for r in self.demo_results) / len(self.demo_results)
        
        print(f"""
📊 DEMO PERFORMANCE METRICS:
   ✅ Scenarios Completed: {successful_scenarios}/{total_scenarios}
   ⏱️  Average Execution Time: {avg_execution_time:.2f}s
   🎯 Total Demo Duration: {total_demo_time/60:.1f} minutes
   🚀 Success Rate: {(successful_scenarios/total_scenarios)*100:.0f}%

🎯 BUSINESS VALUE DELIVERED:

   1. 🚀 SPEED & EFFICIENCY
      • Natural language commands → Immediate governance actions
      • Reduces policy creation from hours to seconds
      • Eliminates manual SQL scripting for governance teams

   2. 🧠 INTELLIGENCE & AUTOMATION
      • AI-powered PII discovery and classification
      • Context-aware masking strategy selection
      • Continuous learning and pattern recognition

   3. 🏗️  INTEGRATION & ORCHESTRATION
      • Seamless Atlan catalog synchronization
      • Multi-mode execution (direct, Airflow, Prefect)
      • Enterprise-grade orchestration capabilities

   4. 🎓 LEARNING & IMPROVEMENT
      • Governance pattern discovery
      • Intelligent recommendations
      • Confidence feedback loops

🎯 POSITIONING SUMMARY:
   Atlan Actions is THE governance automation layer between your
   data catalog and orchestration systems - bridging discovery
   and execution with intelligent automation.
        """)
        
        print(f"\n📈 SCENARIO BREAKDOWN:")
        for i, result in enumerate(self.demo_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {i}. {result['scenario']} ({result['time']:.2f}s)")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Connect your Atlan instance for full catalog integration")
        print(f"   2. Configure Snowflake/BigQuery data sources")
        print(f"   3. Set up Airflow/Prefect for orchestrated governance")
        print(f"   4. Train teams on natural language governance commands")
        
        print(f"\n" + "="*90)
        print(f"🎬 ATLAN ACTIONS ENGINE DEMO COMPLETE")
        print(f"   Thank you for experiencing the future of governance automation!")
        print(f"="*90)

def run_executive_demo():
    """Run the complete executive demo"""
    demo = DemoPresenter()
    demo.demo_start_time = time.time()
    
    try:
        # Setup and introduction
        nl_mode, atlan_enabled = demo.demo_setup_and_intro()
        
        # Initialize Atlan Actions Engine for demo
        atlan_config = None
        if atlan_enabled:
            atlan_config = {
                'base_url': os.getenv('ATLAN_BASE_URL', 'https://demo.atlan.com'),
                'api_token': os.getenv('ATLAN_API_TOKEN')
            }
        
        actions_engine = AtlanActionsEngine(
            execution_mode="direct",
            atlan_config=atlan_config
        )
        
        # Run demo scenarios
        demo.demo_basic_pii_masking(actions_engine)
        demo.demo_autonomous_discovery(actions_engine)
        demo.demo_multi_mode_execution(actions_engine)
        demo.demo_learning_recommendations(actions_engine)
        
        # Summary and conclusion
        demo.demo_summary_and_conclusion()
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo interrupted by user")
        print(f"📊 Completed scenarios: {len(demo.demo_results)}")
        
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        print(f"📊 Completed scenarios: {len(demo.demo_results)}")

def run_quick_demo():
    """Run a condensed 5-minute demo"""
    print("\n" + "="*80)
    print("🎯 ATLAN ACTIONS - QUICK DEMO (5 minutes)")
    print("="*80)
    
    actions_engine = AtlanActionsEngine(execution_mode="direct")
    
    queries = [
        "mask pii in customers table",
        "automatically discover and protect sensitive data"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🚀 Demo {i}/{len(queries)}: {query}")
        
        start_time = time.time()
        results = actions_engine.process_natural_language(query)
        execution_time = time.time() - start_time
        
        status = "✅" if results.get('status') == 'success' else "❌"
        print(f"{status} Completed in {execution_time:.2f}s")
        
        if results.get('status') == 'success':
            exec_result = results['phases'].get('execute', {})
            atlan_status = exec_result.get('atlan_sync_status', {})
            if atlan_status.get('enabled'):
                synced_count = len(atlan_status.get('synced_items', []))
                print(f"🏷️  Synced {synced_count} items to Atlan catalog")
    
    print(f"\n✅ Quick demo complete!")

def main():
    """Demo entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Atlan Actions Engine Demo')
    parser.add_argument('--quick', action='store_true', help='Run 5-minute quick demo')
    parser.add_argument('--full', action='store_true', help='Run full executive demo')
    args = parser.parse_args()
    
    if args.quick:
        run_quick_demo()
    elif args.full:
        run_executive_demo()
    else:
        # Interactive mode
        print("\n🎯 ATLAN ACTIONS ENGINE - DEMO OPTIONS")
        print("="*50)
        print("1. Quick Demo (5 minutes)")
        print("2. Full Executive Demo (15 minutes)")
        print("3. Exit")
        
        choice = input("\nSelect demo type (1-3): ").strip()
        
        if choice == '1':
            run_quick_demo()
        elif choice == '2':
            run_executive_demo()
        else:
            print("👋 Goodbye!")

if __name__ == "__main__":
    main()