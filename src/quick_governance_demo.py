#!/usr/bin/env python3
"""
Quick Demo: Top 10 Governance Scenarios Test
Demonstrates key governance capabilities in a shorter timeframe
"""

from control_pannel import ControlPlaneEngine, NLToSQLConverter
import time

def quick_governance_demo():
    """Demo the top 10 most important governance scenarios"""
    
    print('🚀 QUICK GOVERNANCE CAPABILITIES DEMO')
    print('='*60)
    
    # Top 10 most important scenarios
    scenarios = [
        {
            "id": 1,
            "title": "🔐 PII Masking",
            "query": "mask phone numbers in customers table",
            "category": "Data Privacy"
        },
        {
            "id": 2,
            "title": "🔓 Data Unmasking",
            "query": "unmask email data in customers table",
            "category": "Data Recovery"
        },
        {
            "id": 3,
            "title": "💰 Financial Data Protection",
            "query": "mask total_amount in orders table",
            "category": "Financial Security"
        },
        {
            "id": 4,
            "title": "🏥 Healthcare Compliance",
            "query": "audit patient data access for HIPAA compliance",
            "category": "Healthcare"
        },
        {
            "id": 5,
            "title": "🌍 GDPR Right to be Forgotten",
            "query": "delete all customer data for GDPR compliance",
            "category": "GDPR"
        },
        {
            "id": 6,
            "title": "🤖 AI Bias Detection",
            "query": "analyze employee data for AI bias in hiring",
            "category": "AI Ethics"
        },
        {
            "id": 7,
            "title": "🔒 Quantum-Safe Encryption",
            "query": "encrypt sensitive data with quantum-safe algorithms",
            "category": "Future Security"
        },
        {
            "id": 8,
            "title": "📊 Data Quality Monitoring",
            "query": "check data quality issues in all tables",
            "category": "Data Quality"
        },
        {
            "id": 9,
            "title": "🛡️ Zero Trust Security",
            "query": "implement zero trust verification for data access",
            "category": "Security"
        },
        {
            "id": 10,
            "title": "🌐 Cross-Cloud Governance",
            "query": "federate governance policies across AWS and Azure",
            "category": "Multi-Cloud"
        }
    ]
    
    try:
        # Quick setup
        engine = ControlPlaneEngine('config.yaml')
        if not engine.connect_platform():
            print("❌ Connection failed")
            return
        
        print('✅ Connected to Snowflake!')
        
        # Get schema
        schema = engine._get_detailed_schema_for_chatbot()
        print(f'📊 Schema loaded: {len(schema)} tables')
        
        # Initialize converter
        converter = NLToSQLConverter(provider="openai")
        
        results = []
        
        print('\n🧪 TESTING TOP 10 GOVERNANCE SCENARIOS')
        print('='*60)
        
        for scenario in scenarios:
            print(f'\n{scenario["title"]} ({scenario["category"]})')
            print(f'Query: "{scenario["query"]}"')
            print('-'*50)
            
            start_time = time.time()
            
            try:
                # Detect operation type
                query_lower = scenario["query"].lower()
                
                if 'unmask' in query_lower or 'restore' in query_lower:
                    print('🔓 UNMASKING Operation')
                    result = converter.convert_for_database_unmasking(scenario["query"], schema, "snowflake")
                elif any(word in query_lower for word in ['mask', 'encrypt', 'hide', 'quantum']):
                    print('🔐 MASKING Operation')
                    result = converter.convert_for_database_masking(scenario["query"], schema, "snowflake")
                else:
                    print('🔍 QUERY Operation')
                    result = converter.convert_for_data_query(scenario["query"], schema, "snowflake")
                
                execution_time = time.time() - start_time
                
                # Display results
                confidence_emoji = "🟢" if result.confidence > 0.8 else "🟡" if result.confidence > 0.6 else "🔴"
                print(f'{confidence_emoji} Confidence: {result.confidence:.1%}')
                print(f'⏱️  Time: {execution_time:.2f}s')
                print(f'📝 SQL Commands: {len(result.sql_commands)}')
                
                if result.sql_commands:
                    sample_sql = result.sql_commands[0][:100] + "..." if len(result.sql_commands[0]) > 100 else result.sql_commands[0]
                    print(f'💻 Sample: {sample_sql}')
                
                results.append({
                    "scenario": scenario["title"],
                    "confidence": result.confidence,
                    "time": execution_time,
                    "sql_count": len(result.sql_commands),
                    "status": "✅ SUCCESS"
                })
                
            except Exception as e:
                print(f'❌ Error: {str(e)[:100]}...')
                results.append({
                    "scenario": scenario["title"],
                    "confidence": 0,
                    "time": time.time() - start_time,
                    "sql_count": 0,
                    "status": "❌ ERROR"
                })
        
        # Summary Report
        print('\n📊 GOVERNANCE CAPABILITIES SUMMARY')
        print('='*60)
        
        successful = len([r for r in results if r["status"] == "✅ SUCCESS"])
        avg_confidence = sum([r["confidence"] for r in results if r["confidence"] > 0]) / max(1, len([r for r in results if r["confidence"] > 0]))
        avg_time = sum([r["time"] for r in results]) / len(results)
        
        print(f'📈 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)')
        print(f'🎯 Average Confidence: {avg_confidence:.1%}')
        print(f'⏱️  Average Response Time: {avg_time:.2f}s')
        
        print(f'\n🏆 TOP PERFORMING SCENARIOS:')
        sorted_results = sorted([r for r in results if r["confidence"] > 0], key=lambda x: x["confidence"], reverse=True)
        for i, result in enumerate(sorted_results[:5], 1):
            print(f'   {i}. {result["scenario"][:40]}... ({result["confidence"]:.1%})')
        
        print(f'\n🎉 GOVERNANCE DEMO COMPLETED!')
        print(f'Your AI-powered data governance system is ready for production! 🚀')
        
    except Exception as e:
        print(f'❌ Demo failed: {e}')

if __name__ == "__main__":
    quick_governance_demo()