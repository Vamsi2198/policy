#!/usr/bin/env python3
"""
Chatbot Governance Tester
Tests all 20 governance examples by calling the chatbot one by one
Uses: python control_pannel.py --chatbot
"""

import subprocess
import time
import json
from datetime import datetime
import os

class ChatbotGovernanceTester:
    """Test all 20 governance scenarios through the chatbot interface"""
    
    def __init__(self):
        self.test_scenarios = [
            {
                "id": 1,
                "name": "Automatically discover PII and apply intelligent masking",
                "query": "mask all PII data in the CUSTOMERS table",
                "expected_keywords": ["mask", "pii", "customers"]
            },
            {
                "id": 2,
                "name": "Dynamic access control based on time, location, and data sensitivity",
                "query": "implement dynamic access control for sensitive data based on business hours",
                "expected_keywords": ["access", "control", "dynamic"]
            },
            {
                "id": 3,
                "name": "Track and govern ML model training data lineage",
                "query": "show me the data lineage for ML training datasets",
                "expected_keywords": ["lineage", "ml", "training"]
            },
            {
                "id": 4,
                "name": "Implement GDPR right to be forgotten across all systems",
                "query": "delete all data for customer ID 123 according to GDPR right to be forgotten",
                "expected_keywords": ["gdpr", "delete", "forgotten"]
            },
            {
                "id": 5,
                "name": "Real-time data quality enforcement with automatic remediation",
                "query": "check data quality issues and apply automatic fixes",
                "expected_keywords": ["quality", "remediation", "fixes"]
            },
            {
                "id": 6,
                "name": "Federate governance policies across AWS, Azure, and GCP",
                "query": "federate our governance policies across multiple cloud platforms",
                "expected_keywords": ["federate", "cloud", "policies"]
            },
            {
                "id": 7,
                "name": "AI-powered automatic data classification with confidence scoring",
                "query": "classify all data automatically using AI with confidence scores",
                "expected_keywords": ["classify", "ai", "confidence"]
            },
            {
                "id": 8,
                "name": "Govern data shared with external partners and suppliers",
                "query": "manage data sharing agreements with external partners",
                "expected_keywords": ["sharing", "partners", "external"]
            },
            {
                "id": 9,
                "name": "Real-time compliance for financial trading data",
                "query": "monitor financial trading data for real-time compliance",
                "expected_keywords": ["financial", "trading", "compliance"]
            },
            {
                "id": 10,
                "name": "Automated HIPAA compliance for healthcare data",
                "query": "ensure HIPAA compliance for all healthcare patient data",
                "expected_keywords": ["hipaa", "healthcare", "patient"]
            },
            {
                "id": 11,
                "name": "Govern real-time IoT data streams",
                "query": "manage governance for IoT sensor data streams",
                "expected_keywords": ["iot", "sensor", "streams"]
            },
            {
                "id": 12,
                "name": "Blockchain-based immutable audit trails",
                "query": "implement blockchain audit trails for data access tracking",
                "expected_keywords": ["blockchain", "audit", "immutable"]
            },
            {
                "id": 13,
                "name": "Detect and mitigate AI bias in data and models",
                "query": "detect and fix AI bias in our machine learning models",
                "expected_keywords": ["bias", "ai", "models"]
            },
            {
                "id": 14,
                "name": "Implement quantum-safe encryption for future-proofing",
                "query": "implement quantum-safe encryption to protect against future threats",
                "expected_keywords": ["quantum", "encryption", "future"]
            },
            {
                "id": 15,
                "name": "Federated governance for data mesh architecture",
                "query": "setup federated governance for our data mesh architecture",
                "expected_keywords": ["mesh", "federated", "architecture"]
            },
            {
                "id": 16,
                "name": "Govern synthetic data generation and usage",
                "query": "manage synthetic data generation and ensure proper usage governance",
                "expected_keywords": ["synthetic", "generation", "usage"]
            },
            {
                "id": 17,
                "name": "ESG environmental data compliance monitoring",
                "query": "monitor ESG environmental compliance metrics and reporting",
                "expected_keywords": ["esg", "environmental", "compliance"]
            },
            {
                "id": 18,
                "name": "Governance for distributed edge computing environments",
                "query": "implement governance for edge computing data processing",
                "expected_keywords": ["edge", "computing", "distributed"]
            },
            {
                "id": 19,
                "name": "Zero trust security model for data access",
                "query": "implement zero trust security model for all data access",
                "expected_keywords": ["zero", "trust", "security"]
            },
            {
                "id": 20,
                "name": "Fully autonomous governance system with self-optimization",
                "query": "enable autonomous governance with self-optimization capabilities",
                "expected_keywords": ["autonomous", "self-optimization", "governance"]
            }
        ]
        
        self.results = []
        self.start_time = None
        
    def run_chatbot_command(self, query: str, timeout: int = 60) -> dict:
        """Run a single chatbot command and capture the response"""
        
        try:
            # Prepare the command
            cmd = ['python', 'control_pannel.py', '--chatbot']
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                cwd=os.getcwd(),
                bufsize=1,
                universal_newlines=True
            )
            
            # Prepare input - include confirmation for masking operations
            input_lines = [
                query,
                "yes",  # Confirm any masking operations
                "y",    # Additional confirmation
                "exit"  # Exit the chatbot
            ]
            input_text = "\n".join(input_lines) + "\n"
            
            # Get the output with timeout
            stdout, stderr = process.communicate(input=input_text, timeout=timeout)
            
            return {
                'success': True,
                'stdout': stdout,
                'stderr': stderr or '',
                'return_code': process.returncode,
                'full_output': stdout
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return {
                'success': False,
                'error': 'Command timed out',
                'timeout': timeout,
                'partial_output': stdout or ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_single_scenario(self, scenario: dict) -> dict:
        """Test a single governance scenario"""
        
        print(f"\n🔄 **Example {scenario['id']:02d}:** {scenario['name']}")
        print(f"📝 Query: '{scenario['query']}'")
        
        start_time = time.time()
        
        # Run the chatbot command
        result = self.run_chatbot_command(scenario['query'])
        
        execution_time = time.time() - start_time
        
        # Analyze the result
        if result['success']:
            output = result.get('full_output', result.get('stdout', ''))
            
            # Look for key indicators of successful processing
            success_indicators = [
                'Generated SQL:',
                'MASKING COMPLETED',
                'Results (',
                'Confidence:',
                'Processing:',
                'rows masked:',
                'Executing query',
                '✅',
                'SUCCESS'
            ]
            
            # Check for governance-specific outputs
            governance_indicators = [
                'masking',
                'compliance',
                'governance',
                'policy',
                'audit',
                'security',
                'privacy',
                'encryption',
                'classification'
            ]
            
            # Count indicators found
            success_count = sum(1 for indicator in success_indicators 
                              if indicator.lower() in output.lower())
            
            governance_count = sum(1 for indicator in governance_indicators 
                                 if indicator.lower() in output.lower())
            
            # Check for expected keywords from scenario
            keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                               if keyword.lower() in output.lower())
            
            # Determine success based on multiple criteria
            has_meaningful_output = len(output.strip()) > 100
            has_sql_or_results = any(sql_word in output.lower() for sql_word in 
                                   ['select', 'update', 'insert', 'delete', 'results', 'rows'])
            
            scenario_success = (
                success_count >= 2 or
                governance_count >= 1 or
                keywords_found >= len(scenario['expected_keywords']) // 2 or
                has_sql_or_results
            ) and has_meaningful_output
            
            if scenario_success:
                print(f"✅ Success - Indicators: {success_count}, Governance: {governance_count}, Keywords: {keywords_found}")
                status = 'SUCCESS'
            else:
                print(f"⚠️ Partial Success - Limited indicators found")
                status = 'PARTIAL'
            
            # Show relevant output snippets
            if output.strip():
                # Extract key parts of the output
                lines = output.split('\n')
                important_lines = []
                
                for line in lines:
                    line = line.strip()
                    if any(keyword in line.lower() for keyword in 
                          ['generated sql', 'masking completed', 'results', 'confidence', 
                           'processing', 'executing', '✅', 'rows masked']):
                        important_lines.append(line)
                
                if important_lines:
                    print(f"📄 Key Output:")
                    for line in important_lines[-3:]:  # Show last 3 important lines
                        if line:
                            print(f"    {line[:80]}...")
                else:
                    # Fallback to showing last few non-empty lines
                    non_empty_lines = [line.strip() for line in lines if line.strip()]
                    if non_empty_lines:
                        print(f"📄 Response: {non_empty_lines[-1][:80]}...")
            
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            if 'partial_output' in result:
                print(f"📄 Partial Output: {result['partial_output'][:100]}...")
            status = 'ERROR'
        
        test_result = {
            'scenario_id': scenario['id'],
            'name': scenario['name'],
            'query': scenario['query'],
            'status': status,
            'execution_time': execution_time,
            'result': result
        }
        
        self.results.append(test_result)
        return test_result
    
    def run_all_scenarios(self):
        """Run all 20 governance scenarios"""
        
        print('🚀 CHATBOT GOVERNANCE TESTING SUITE')
        print('🤖 Testing all 20 scenarios through control_pannel.py --chatbot')
        print('='*80)
        
        self.start_time = time.time()
        
        # Test each scenario
        for scenario in self.test_scenarios:
            try:
                self.test_single_scenario(scenario)
                time.sleep(2)  # Longer pause between tests to allow chatbot to fully initialize
                
            except KeyboardInterrupt:
                print(f"\n⚠️ Testing interrupted by user after scenario {scenario['id']}")
                break
            except Exception as e:
                print(f"❌ Unexpected error in scenario {scenario['id']}: {e}")
                continue
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        
        total_time = time.time() - self.start_time if self.start_time else 0
        
        print('\n📊 CHATBOT GOVERNANCE TEST REPORT')
        print('='*80)
        
        # Summary statistics
        total_tests = len(self.results)
        successful = len([r for r in self.results if r['status'] == 'SUCCESS'])
        partial = len([r for r in self.results if r['status'] == 'PARTIAL'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print(f'📈 EXECUTION SUMMARY:')
        print(f'   Total Tests Run: {total_tests}/20')
        print(f'   ✅ Successful: {successful} ({successful/total_tests*100:.1f}%)' if total_tests > 0 else '   ✅ Successful: 0')
        print(f'   ⚠️ Partial: {partial} ({partial/total_tests*100:.1f}%)' if total_tests > 0 else '   ⚠️ Partial: 0')
        print(f'   ❌ Errors: {errors} ({errors/total_tests*100:.1f}%)' if total_tests > 0 else '   ❌ Errors: 0')
        print(f'   ⏱️ Total Execution Time: {total_time:.2f}s')
        
        if total_tests > 0:
            avg_time = sum(r['execution_time'] for r in self.results) / total_tests
            print(f'   ⏱️ Average Test Time: {avg_time:.2f}s')
        
        # Detailed results
        print(f'\n📋 DETAILED RESULTS:')
        for result in self.results:
            status_icon = '✅' if result['status'] == 'SUCCESS' else '⚠️' if result['status'] == 'PARTIAL' else '❌'
            print(f'   {status_icon} Example {result["scenario_id"]:02d}: {result["name"][:60]}...')
        
        # Governance capabilities tested
        print(f'\n🛡️ GOVERNANCE CAPABILITIES TESTED:')
        capabilities = [
            'PII Masking & Data Privacy',
            'Dynamic Access Control',
            'ML Governance & Lineage',
            'GDPR Compliance',
            'Real-time Data Quality',
            'Multi-Cloud Federation',
            'AI-Powered Classification',
            'External Data Sharing',
            'Financial Compliance',
            'Healthcare HIPAA',
            'IoT Data Governance',
            'Blockchain Audit Trails',
            'AI Bias Detection',
            'Quantum-Safe Encryption',
            'Data Mesh Architecture',
            'Synthetic Data Governance',
            'ESG Compliance',
            'Edge Computing Governance',
            'Zero Trust Security',
            'Autonomous Governance'
        ]
        
        for i, capability in enumerate(capabilities[:total_tests], 1):
            result = next((r for r in self.results if r['scenario_id'] == i), None)
            if result:
                status_icon = '✅' if result['status'] == 'SUCCESS' else '⚠️' if result['status'] == 'PARTIAL' else '❌'
                print(f'   {status_icon} {capability}')
        
        # Final assessment
        print(f'\n🎉 FINAL ASSESSMENT:')
        if total_tests == 0:
            print('   ⚠️ No tests completed - check chatbot connectivity')
        elif successful >= 16:  # 80% success rate
            print('   🌟 EXCELLENT: Chatbot governance system is highly functional!')
            print('   🚀 Most governance capabilities working through natural language')
            print('   ✅ Ready for production governance operations')
        elif successful >= 12:  # 60% success rate
            print('   👍 GOOD: Chatbot handles most governance scenarios well')
            print('   🔧 Some capabilities may need refinement')
            print('   ✅ Ready for pilot governance operations')
        else:
            print('   ⚠️ NEEDS IMPROVEMENT: Several chatbot responses need attention')
            print('   🔧 Review chatbot logic and governance implementations')
            print('   🧪 Continue testing and refinement')
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'chatbot_governance_results_{timestamp}.json'
        
        try:
            with open(results_file, 'w') as f:
                json.dump({
                    'test_summary': {
                        'total_tests': total_tests,
                        'successful': successful,
                        'partial': partial,
                        'errors': errors,
                        'success_rate': successful/total_tests if total_tests > 0 else 0,
                        'total_execution_time': total_time,
                        'timestamp': datetime.now().isoformat()
                    },
                    'test_results': self.results
                }, f, indent=2)
            
            print(f'\n💾 Detailed results saved to: {results_file}')
            
        except Exception as e:
            print(f'\n⚠️ Could not save results file: {e}')
        
        print('='*80)

def main():
    """Main execution function"""
    
    print('🌟 WELCOME TO CHATBOT GOVERNANCE TESTER')
    print('🤖 Testing all 20 governance scenarios through the chatbot interface')
    print('📋 Each test calls: python control_pannel.py --chatbot')
    print('⏱️ Estimated time: 3-5 minutes for all scenarios')
    print('\nPress Ctrl+C to interrupt if needed...\n')
    
    try:
        tester = ChatbotGovernanceTester()
        tester.run_all_scenarios()
        
    except KeyboardInterrupt:
        print('\n⚠️ Testing interrupted by user')
        print('📊 Partial results may be available')
    except Exception as e:
        print(f'\n❌ Testing failed: {e}')

if __name__ == "__main__":
    main()