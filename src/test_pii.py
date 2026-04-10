#!/usr/bin/env python3
"""Quick test of PII masking scenario"""

from control_pannel import ControlPlaneEngine

def test_pii_masking():
    """Test PII masking scenario quickly"""
    
    print('🔐 TESTING PII MASKING SCENARIO')
    print('='*50)
    
    engine = ControlPlaneEngine('config.yaml')
    
    if engine.connect_platform():
        print('✅ Connected to Snowflake')
        
        # Run PII masking scenario
        print('\n🚀 Running PII Masking Scenario...')
        try:
            result = engine.run_scenario_01_pii_masking()
            
            print(f'\n📊 RESULTS:')
            print(f'✅ Success: {result.success}')
            print(f'⏱️  Time: {result.execution_time:.2f}s')
            print(f'📈 Metrics:')
            
            for key, value in result.metrics.items():
                print(f'   • {key}: {value}')
            
            if result.errors:
                print(f'\n❌ Errors:')
                for error in result.errors:
                    print(f'   • {error}')
                    
        except KeyboardInterrupt:
            print('\n⚠️ Test interrupted by user')
        except Exception as e:
            print(f'\n❌ Error: {e}')
    else:
        print('❌ Failed to connect to database')

if __name__ == "__main__":
    test_pii_masking()