#!/usr/bin/env python3
"""
S3 Data Handler
===============
Loads data from s3.json and applies runtime policies based on user queries.
Then inserts the modified data into Snowflake my_table.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class PolicyApplication:
    """Result of applying a policy to data"""
    original_data: List[Dict[str, Any]]
    masked_data: List[Dict[str, Any]]
    policies_applied: List[Dict[str, str]]
    affected_fields: List[str]

class S3DataHandler:
    """Handles loading S3 data and applying runtime policies"""
    
    def __init__(self, s3_json_path: str = None):
        """
        Initialize S3 Data Handler
        
        Args:
            s3_json_path: Path to s3.json file. If None, will search in common locations.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Find s3.json file
        if s3_json_path and os.path.exists(s3_json_path):
            self.s3_json_path = s3_json_path
        else:
            # Search in common locations
            search_paths = [
                "s3.json",
                "src/s3.json",
                "../s3.json",
                os.path.join(os.path.dirname(__file__), "s3.json"),
                os.path.join(os.path.dirname(__file__), "..", "s3.json")
            ]
            
            self.s3_json_path = None
            for path in search_paths:
                if os.path.exists(path):
                    self.s3_json_path = path
                    break
            
            if not self.s3_json_path:
                raise FileNotFoundError(f"s3.json not found in any of these locations: {search_paths}")
        
        self.logger.info(f"✅ S3 Data Handler initialized with file: {self.s3_json_path}")
        self.original_data = self.load_s3_data()
        
    def load_s3_data(self) -> List[Dict[str, Any]]:
        """Load data from s3.json file"""
        try:
            with open(self.s3_json_path, 'r') as f:
                data = json.load(f)
            self.logger.info(f"✅ Loaded {len(data)} records from {self.s3_json_path}")
            return data
        except Exception as e:
            self.logger.error(f"❌ Failed to load s3.json: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Extract schema from S3 data"""
        if not self.original_data:
            return {}
        
        # Get first record to determine schema
        sample = self.original_data[0]
        schema = {
            "table_name": "S3_DATA",
            "columns": []
        }
        
        for key, value in sample.items():
            col_info = {
                "name": key.upper(),
                "type": self._infer_type(value),
                "nullable": True
            }
            schema["columns"].append(col_info)
        
        return schema
    
    def _infer_type(self, value: Any) -> str:
        """Infer SQL type from Python value"""
        if isinstance(value, int):
            return "NUMBER"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, str):
            return "VARCHAR"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "VARCHAR"
    
    def apply_masking_policies(self, user_query: str, pii_findings: List[Dict[str, Any]] = None) -> PolicyApplication:
        """
        Apply masking policies to S3 data based on user query and PII findings
        
        Args:
            user_query: Natural language query from user
            pii_findings: Optional list of PII findings from analyzer
            
        Returns:
            PolicyApplication with original and masked data
        """
        import copy
        
        masked_data = copy.deepcopy(self.original_data)
        policies_applied = []
        affected_fields = []
        
        # Detect fields to mask from user query (fully dynamic)
        fields_to_mask = self._detect_fields_to_mask(user_query, pii_findings)
        
        self.logger.info(f"🎯 Query: '{user_query}' → Detected {len(fields_to_mask)} fields to mask: {[f['field'] for f in fields_to_mask]}")
        
        for field_info in fields_to_mask:
            field_name = field_info['field']
            mask_type = field_info['type']
            
            # Apply masking to all records
            for record in masked_data:
                if field_name in record:
                    original_value = record[field_name]
                    record[field_name] = self._apply_mask(original_value, mask_type)
            
            policies_applied.append({
                'field': field_name,
                'policy': f"MASK_{mask_type.upper()}",
                'type': mask_type
            })
            affected_fields.append(field_name)
        
        self.logger.info(f"✅ Applied {len(policies_applied)} masking policies to {len(masked_data)} records")
        
        return PolicyApplication(
            original_data=self.original_data,
            masked_data=masked_data,
            policies_applied=policies_applied,
            affected_fields=affected_fields
        )
    
    def _detect_fields_to_mask(self, user_query: str, pii_findings: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Detect which fields need masking ONLY from user query - fully dynamic"""
        fields_to_mask = []
        query_lower = user_query.lower()
        
        # Common PII patterns in queries
        pii_patterns = {
            'email': r'\b(email|e-mail|mail)\b',
            'ssn': r'\b(ssn|social\s*security|social\s*security\s*number)\b',
            'salary': r'\b(salary|compensation|pay|income)\b',
            'address': r'\b(address|location|street|residence)\b',
            'phone': r'\b(phone|telephone|mobile|cell)\b',
            'name': r'\b(name|firstname|lastname|full\s*name)\b'
        }
        
        # Check if user wants ALL PII masked
        mask_all_pii = re.search(r'\b(all|every|everything|entire)\s*(pii|sensitive|personal|data)', query_lower)
        
        if mask_all_pii:
            # Mask all detected PII fields
            if pii_findings:
                for finding in pii_findings:
                    field = finding.get('column') or finding.get('field')
                    pii_type = finding.get('pii_type', 'generic')
                    if field and {'field': field, 'type': pii_type} not in fields_to_mask:
                        fields_to_mask.append({'field': field, 'type': pii_type})
            else:
                # Fallback: mask common PII fields
                for field in self.original_data[0].keys():
                    field_lower = field.lower()
                    if any(pii in field_lower for pii in ['email', 'ssn', 'salary', 'address', 'phone', 'name']):
                        pii_type = next((pii for pii in ['email', 'ssn', 'salary', 'address', 'phone', 'name'] if pii in field_lower), 'generic')
                        if {'field': field, 'type': pii_type} not in fields_to_mask:
                            fields_to_mask.append({'field': field, 'type': pii_type})
        else:
            # ONLY mask fields explicitly mentioned in query
            for pii_type, pattern in pii_patterns.items():
                if re.search(pattern, query_lower):
                    # Find matching field in data
                    for field in self.original_data[0].keys():
                        if pii_type in field.lower():
                            if {'field': field, 'type': pii_type} not in fields_to_mask:
                                fields_to_mask.append({'field': field, 'type': pii_type})
        
        return fields_to_mask
    
    def _apply_mask(self, value: Any, mask_type: str) -> str:
        """Apply dynamic masking transformation based on data type"""
        if value is None:
            return None
        
        value_str = str(value)
        
        if mask_type == 'email':
            # Mask email: a***@***.com
            if '@' in value_str:
                parts = value_str.split('@')
                if parts[0] and parts[1]:
                    domain_parts = parts[1].split('.')
                    masked_domain = f"{domain_parts[0][0]}***" if domain_parts[0] else "***"
                    return f"{parts[0][0]}***@{masked_domain}.{domain_parts[-1]}" if len(domain_parts) > 1 else f"{parts[0][0]}***@{masked_domain}"
            return "***@***.com"
        
        elif mask_type == 'ssn':
            # Mask SSN: ***-**-6789
            if '-' in value_str:
                parts = value_str.split('-')
                return f"***-**-{parts[-1]}" if len(parts) == 3 else "***-**-****"
            elif len(value_str) >= 4:
                return f"***-**-{value_str[-4:]}"
            return "***-**-****"
        
        elif mask_type == 'salary':
            # Keep salary as-is (no masking by default unless explicitly requested)
            return value
        
        elif mask_type == 'address':
            # Mask address: keep last few chars
            if len(value_str) > 5:
                return f"{value_str[:2]}***{value_str[-3:]}"
            return "***"
        
        elif mask_type == 'phone':
            # Mask phone: ***-***-1234
            if len(value_str) >= 4:
                return f"***-***-{value_str[-4:]}"
            return "***-***-****"
        
        elif mask_type == 'name':
            # Mask name: keep first 2 letters, last 2 letters
            parts = value_str.split()
            if len(parts) > 1:
                return f"{parts[0][:2]}***{parts[0][-2:]} {parts[-1][:2]}***{parts[-1][-2:]}" if len(parts[0]) > 3 and len(parts[-1]) > 3 else f"{parts[0][:2]}*** {parts[-1][:2]}***"
            elif len(value_str) > 3:
                return f"{value_str[:2]}***{value_str[-2:]}"
            return "***"
        
        else:
            # Generic masking - preserve first and last chars
            if len(value_str) > 4:
                return f"{value_str[:2]}***{value_str[-2:]}"
            return "***"
    
    def prepare_for_snowflake_insert(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare data for insertion into Snowflake my_table (id INT, data STRING)
        
        Args:
            data: List of records to insert
            
        Returns:
            List of dicts with 'id' and 'data' fields
        """
        snowflake_records = []
        
        for idx, record in enumerate(data, start=1):
            snowflake_record = {
                'id': idx,
                'data': json.dumps(record)  # Convert entire record to JSON string
            }
            snowflake_records.append(snowflake_record)
        
        return snowflake_records
    
    def get_sample_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample data for preview"""
        return self.original_data[:limit]
    
    def get_column_sample(self, column_name: str, limit: int = 100) -> List[Any]:
        """Get sample values for a specific column"""
        values = []
        for record in self.original_data[:limit]:
            if column_name in record:
                values.append(record[column_name])
        return values


class SnowflakeInserter:
    """Handles inserting data into Snowflake my_table"""
    
    def __init__(self, snowflake_connector):
        """
        Initialize Snowflake inserter
        
        Args:
            snowflake_connector: Active Snowflake connection from control_pannel
        """
        self.connector = snowflake_connector
        self.logger = logging.getLogger(self.__class__.__name__)
        self.table_name = "MY_TABLE"
        
        # Validate connector
        if not self._validate_connector():
            raise ValueError("Invalid Snowflake connector provided")
    
    def _validate_connector(self) -> bool:
        """Validate that connector is properly initialized"""
        if self.connector is None:
            self.logger.error("❌ Connector is None")
            return False
        
        # Check if connector has connection attribute
        if not hasattr(self.connector, 'connection'):
            self.logger.error("❌ Connector missing 'connection' attribute")
            return False
        
        if self.connector.connection is None:
            self.logger.error("❌ Connector connection is None - not connected to Snowflake")
            return False
        
        return True
    
    def _execute_sql(self, sql: str):
        """Execute SQL with proper error handling"""
        if hasattr(self.connector, 'execute'):
            return self.connector.execute(sql)
        elif hasattr(self.connector, 'connection'):
            cursor = self.connector.connection.cursor()
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
                cursor.close()
                return result
            except Exception as e:
                cursor.close()
                raise e
        else:
            raise AttributeError("Connector has no execute method or connection")
    
    def ensure_table_exists(self) -> bool:
        """Ensure my_table exists in Snowflake"""
        try:
            create_sql = """
            CREATE TABLE IF NOT EXISTS MY_TABLE (
                id INT,
                data STRING
            )
            """
            self._execute_sql(create_sql)
            self.logger.info("✅ Ensured MY_TABLE exists in Snowflake")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create MY_TABLE: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def clear_table(self) -> bool:
        """Clear all data from my_table"""
        try:
            self._execute_sql("DELETE FROM MY_TABLE")
            self.logger.info("✅ Cleared MY_TABLE")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to clear MY_TABLE: {e}")
            return False
    
    def insert_data(self, records: List[Dict[str, Any]], clear_first: bool = True) -> Dict[str, Any]:
        """
        Insert data into my_table
        
        Args:
            records: List of dicts with 'id' and 'data' keys
            clear_first: Whether to clear table before inserting
            
        Returns:
            Dict with insertion results
        """
        try:
            # Ensure table exists
            if not self.ensure_table_exists():
                return {
                    'success': False,
                    'error': 'Failed to create table',
                    'rows_inserted': 0
                }
            
            # Clear table if requested
            if clear_first:
                self.clear_table()
            
            # Insert records
            rows_inserted = 0
            for record in records:
                insert_sql = f"""
                INSERT INTO MY_TABLE (id, data)
                VALUES ({record['id']}, '{record['data'].replace("'", "''")}')
                """
                self._execute_sql(insert_sql)
                rows_inserted += 1
            
            self.logger.info(f"✅ Inserted {rows_inserted} rows into MY_TABLE")
            
            return {
                'success': True,
                'rows_inserted': rows_inserted,
                'table_name': self.table_name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to insert data: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'rows_inserted': 0
            }
    
    def verify_insertion(self) -> Dict[str, Any]:
        """Verify data was inserted correctly"""
        try:
            count_result = self._execute_sql("SELECT COUNT(*) as cnt FROM MY_TABLE")
            sample_result = self._execute_sql("SELECT * FROM MY_TABLE LIMIT 5")
            
            # Parse count result
            if isinstance(count_result, list) and len(count_result) > 0:
                if isinstance(count_result[0], dict):
                    total_rows = count_result[0].get('CNT', 0)
                elif isinstance(count_result[0], tuple):
                    total_rows = count_result[0][0]
                else:
                    total_rows = count_result[0]
            else:
                total_rows = 0
            
            # Parse sample result
            sample_data = []
            if isinstance(sample_result, list):
                for row in sample_result[:5]:
                    if isinstance(row, dict):
                        sample_data.append(row)
                    elif isinstance(row, tuple) and len(row) >= 2:
                        sample_data.append({'ID': row[0], 'DATA': row[1]})
            
            return {
                'total_rows': total_rows,
                'sample_data': sample_data
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to verify insertion: {e}")
            return {
                'total_rows': 0,
                'sample_data': [],
                'error': str(e)
            }


# Convenience functions
def load_s3_data(s3_json_path: str = None) -> S3DataHandler:
    """Load S3 data handler"""
    return S3DataHandler(s3_json_path)

def apply_policies_and_insert(user_query: str, snowflake_connector, pii_findings: List[Dict] = None) -> Dict[str, Any]:
    """
    Complete workflow: Load S3 data -> Apply policies -> Insert to Snowflake
    
    Args:
        user_query: Natural language query
        snowflake_connector: Active Snowflake connection
        pii_findings: Optional PII findings from analyzer
        
    Returns:
        Dict with complete results
    """
    logger = logging.getLogger("S3Pipeline")
    
    try:
        # Load S3 data
        s3_handler = S3DataHandler()
        logger.info(f"📂 Loaded {len(s3_handler.original_data)} records from S3")
        
        # Apply masking policies
        policy_result = s3_handler.apply_masking_policies(user_query, pii_findings)
        logger.info(f"🔒 Applied {len(policy_result.policies_applied)} policies")
        
        # Prepare for Snowflake
        snowflake_records = s3_handler.prepare_for_snowflake_insert(policy_result.masked_data)
        logger.info(f"📊 Prepared {len(snowflake_records)} records for Snowflake")
        
        # Insert into Snowflake
        inserter = SnowflakeInserter(snowflake_connector)
        insert_result = inserter.insert_data(snowflake_records)
        
        # Verify insertion
        verification = inserter.verify_insertion()
        
        return {
            'success': insert_result['success'],
            'source': 'S3',
            'original_records': len(s3_handler.original_data),
            'masked_records': len(policy_result.masked_data),
            'policies_applied': policy_result.policies_applied,
            'affected_fields': policy_result.affected_fields,
            'snowflake_insertion': insert_result,
            'verification': verification,
            'sample_original': s3_handler.get_sample_data(3),
            'sample_masked': policy_result.masked_data[:3]
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }
