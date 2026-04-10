#!/usr/bin/env python3
"""
Simple Chatbot Governance Tester
Tests governance scenarios through direct chatbot calls with proper encoding
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime

class SimpleChatbotTester:
    """Test governance scenarios through direct chatbot interaction"""
    
    def __init__(self):
        self.test_scenarios = [
            "mask all PII data in the CUSTOMERS table",
            "implement dynamic access control for sensitive data",
            "show me the data lineage for ML training datasets", 
            "delete all data for customer ID 123 according to GDPR",
            "check data quality issues and apply automatic fixes",
            "federate our governance policies across multiple clouds",
            "classify all data automatically using AI",
            "manage data sharing agreements with external partners",
            "monitor financial trading data for compliance",
            "ensure HIPAA compliance for healthcare data",
            "manage governance for IoT sensor data streams",
            "implement blockchain audit trails for data access",
            "detect and fix AI bias in machine learning models",
            "implement quantum-safe encryption for security",
            "setup federated governance for data mesh architecture",
            "manage synthetic data generation and governance",
            "monitor ESG environmental compliance metrics",
            "implement governance for edge computing data",
            "implement zero trust security for data access",
            "enable autonomous governance with self-optimization"
        ]
        
        self.results = []
    
    def run_single_test(self, query: str, test_id: int) -> dict:
        """Run a single governance test"""
        
        print(f"\n🔄 **Example {test_id:02d}:** {query}")
        
        try:
            # Set environment for proper encoding
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # Run the chatbot with the query
            cmd = [sys.executable, 'control_pannel.py', '--chatbot']
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters
                env=env
            )
            
            # Send the query with confirmation
            input_text = f"{query}\nyes\nexit\n"
            
            stdout, _ = process.communicate(input=input_text, timeout=45)
            
            # Analyze the output
            success_indicators = [
                'Generated SQL',
                'MASKING COMPLETED', 
                'Results (',
                'Confidence:',
                'Processing:',
                'rows masked',
                'Executing query',
                'SUCCESS',
                'COMPLETED'
            ]
            
            found_indicators = [indicator for indicator in success_indicators 
                              if indicator.lower() in stdout.lower()]
            
            has_meaningful_response = len(stdout.strip()) > 200
            has_sql = any(word in stdout.lower() for word in ['select', 'update', 'insert', 'delete'])
            
            if found_indicators and has_meaningful_response:
                print(f"✅ SUCCESS - Found indicators: {', '.join(found_indicators[:3])}")
                status = 'SUCCESS'
            elif has_sql or has_meaningful_response:
                print(f"⚠️ PARTIAL - Some response detected")
                status = 'PARTIAL'
            else:
                print(f"❌ FAILED - No meaningful response")
                status = 'FAILED'
            
            # Show key output
            important_lines = []
            for line in stdout.split('\n'):
                if any(keyword in line.lower() for keyword in 
                      ['generated sql', 'masking completed', 'results', 'confidence', 'processing']):
                    important_lines.append(line.strip())
            
            if important_lines:
                print(f"📄 Key Output:")
                for line in important_lines[-2:]:  # Show last 2 important lines
                    if line:
                        print(f"    {line[:100]}")
            
            return {
                'test_id': test_id,
                'query': query,
                'status': status,
                'indicators_found': len(found_indicators),
                'output_length': len(stdout),
                'key_output': important_lines[-1] if important_lines else '',
                'full_output': stdout[:1000]  # First 1000 chars for logging
            }
            
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT - Test took too long")
            return {
                'test_id': test_id,
                'query': query, 
                'status': 'TIMEOUT',
                'error': 'Test timed out'
            }
        except Exception as e:
            print(f"❌ ERROR - {e}")
            return {
                'test_id': test_id,
                'query': query,
                'status': 'ERROR', 
                'error': str(e)
            }
    
    def run_all_tests(self):
        """Run all governance tests"""
        
        print('🚀 SIMPLE CHATBOT GOVERNANCE TESTER')
        print('🤖 Testing governance scenarios with proper encoding')
        print('='*70)
        
        start_time = time.time()
        
        for i, query in enumerate(self.test_scenarios, 1):
            result = self.run_single_test(query, i)
            self.results.append(result)
            
            # Brief pause between tests
            time.sleep(1)
            
            # Stop early if too many failures
            failures = len([r for r in self.results if r['status'] in ['FAILED', 'ERROR']])
            if failures >= 5 and i >= 5:
                print(f"\n⚠️ Stopping early due to {failures} failures")
                break
        
        # Generate report
        self.generate_report(time.time() - start_time)
    
    def generate_report(self, total_time: float):
        """Generate test report"""
        
        print('\n📊 CHATBOT GOVERNANCE TEST REPORT')
        print('='*70)
        
        # Count results
        total = len(self.results)
        success = len([r for r in self.results if r['status'] == 'SUCCESS'])
        partial = len([r for r in self.results if r['status'] == 'PARTIAL'])
        failed = len([r for r in self.results if r['status'] == 'FAILED'])
        errors = len([r for r in self.results if r['status'] in ['ERROR', 'TIMEOUT']])
        
        print(f'📈 SUMMARY:')
        print(f'   Tests Run: {total}/20')
        print(f'   ✅ Success: {success} ({success/total*100:.1f}%)' if total > 0 else '   ✅ Success: 0')
        print(f'   ⚠️ Partial: {partial} ({partial/total*100:.1f}%)' if total > 0 else '   ⚠️ Partial: 0')
        print(f'   ❌ Failed: {failed + errors} ({(failed + errors)/total*100:.1f}%)' if total > 0 else '   ❌ Failed: 0')
        print(f'   ⏱️ Total Time: {total_time:.1f}s')
        
        print(f'\n📋 DETAILED RESULTS:')
        for result in self.results:
            status_icon = {'SUCCESS': '✅', 'PARTIAL': '⚠️', 'FAILED': '❌', 'ERROR': '❌', 'TIMEOUT': '⏰'}.get(result['status'], '❓')
            print(f'   {status_icon} Test {result["test_id"]:02d}: {result["query"][:50]}...')
            if result.get('key_output'):
                print(f'       💬 {result["key_output"][:60]}...')
        
        # Assessment
        print(f'\n🎯 ASSESSMENT:')
        if success >= 15:
            print('   🌟 EXCELLENT: Chatbot governance is working great!')
        elif success >= 10:
            print('   👍 GOOD: Most governance features working through chatbot')
        elif success >= 5:
            print('   ⚠️ MIXED: Some governance features working, needs improvement')
        else:
            print('   🔧 NEEDS WORK: Chatbot governance needs debugging')
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'simple_chatbot_results_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'summary': {
                        'total_tests': total,
                        'success': success,
                        'partial': partial,
                        'failed': failed,
                        'errors': errors,
                        'total_time': total_time
                    },
                    'results': self.results
                }, f, indent=2)
            
            print(f'\n💾 Results saved to: {filename}')
        except Exception as e:
            print(f'\n⚠️ Could not save results: {e}')
        
        print('='*70)

def main():
    """Run the simple chatbot tester"""
    
    print('🌟 WELCOME TO SIMPLE CHATBOT GOVERNANCE TESTER')
    print('🤖 This tester handles encoding issues and provides clear results')
    print('⏱️ Estimated time: 2-3 minutes for 20 tests')
    print('\nPress Ctrl+C to interrupt...\n')
    
    try:
        tester = SimpleChatbotTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print('\n⚠️ Testing interrupted by user')
    except Exception as e:
        print(f'\n❌ Testing failed: {e}')

if __name__ == "__main__":
    main()