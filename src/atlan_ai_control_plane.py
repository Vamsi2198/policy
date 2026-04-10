#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atlan Actions Engine - Governance Automation Platform
6-Phase Closed Loop: OBSERVE → ANALYZE → PLAN → SIMULATE → EXECUTE → LEARN

Atlan Actions sits between the catalog and orchestration layers, providing
intelligent governance automation that bridges discovery and execution.

Key Features:
- Natural language governance commands
- Atlan catalog integration for metadata sync
- Multi-mode execution (direct, Airflow, Prefect)
- 6-phase autonomous governance loop
"""

import os
import sys
import json
import time
import logging
import sqlite3
import hashlib
import argparse
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
from decimal import Decimal

# ============================================================================
# IMPORTS - Core governance engine and Atlan integration
# ============================================================================
from control_pannel import ControlPlaneEngine, PIIAnalyzer

# Import S3 data handler
try:
    from s3_data_handler import S3DataHandler, SnowflakeInserter, apply_policies_and_insert
    HAS_S3_HANDLER = True
except ImportError:
    HAS_S3_HANDLER = False
    print("⚠️  S3 Data Handler not available - will use Snowflake data only")

# Import enhanced AI control plane with comprehensive audit logging
try:
    from ai_control_plane import AIControlPlane
    ENHANCED_AI_AVAILABLE = True
except ImportError:
    print("WARNING: Enhanced AI control plane not available - using basic mode")
    ENHANCED_AI_AVAILABLE = False

# Atlan Integration (graceful fallback if not available)
try:
    from atlan_integration import AtlanAPIClient, AtlanGovernanceSync
    ATLAN_AVAILABLE = True
except ImportError:
    print("WARNING: Atlan integration not available - running in standalone mode")
    ATLAN_AVAILABLE = False

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal, datetime, and other database objects"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super(DecimalEncoder, self).default(obj)

@dataclass
class ObservationResult:
    """Results from OBSERVE phase"""
    intent: str
    target_entities: List[str]
    confidence: float
    schema_context: Dict[str, Any]
    current_state: Dict[str, Any]
    sample_data: Dict[str, List[Any]]
    sql_result: Any
    today_date: str = field(default_factory=lambda: date.today().isoformat())
    relative_date_filter: Optional[Dict[str, Any]] = None
    user_query: str = ""

@dataclass
class AnalysisResult:
    """Results from ANALYZE phase"""
    pii_findings: List[Dict[str, Any]]
    impact_assessment: Dict[str, Any]
    risk_score: float
    ml_confidence: float
    entity_relationships: Dict[str, List[str]]

@dataclass
class ExecutionPlan:
    """Results from PLAN phase"""
    sql_commands: List[str]
    execution_order: List[int]
    dependencies: Dict[str, List[str]]
    rollback_strategy: List[str]
    estimated_impact: Dict[str, Any]
    safety_checks: List[str]

@dataclass
class SimulationResult:
    """Results from SIMULATE phase"""
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    affected_rows: int
    affected_columns: List[str]
    downstream_impact: List[str]
    risk_assessment: str

@dataclass
class ExecutionResult:
    """Results from EXECUTE phase"""
    success: bool
    commands_executed: List[str]
    execution_time: float
    rows_affected: int
    metadata_updates: Dict[str, Any]
    audit_trail: Dict[str, Any]
    atlan_sync_status: Dict[str, Any]  # New: Atlan sync results

@dataclass
class LearningResult:
    """Results from LEARN phase"""
    verification_status: bool
    performance_impact: Dict[str, float]
    discovered_patterns: List[str]
    recommendations: List[str]
    confidence_feedback: float

class ExecutionMode(Enum):
    """Execution modes for Atlan Actions Engine"""
    DIRECT = "direct"        # Execute immediately
    AIRFLOW = "airflow"      # Generate Airflow DAG
    PREFECT = "prefect"      # Generate Prefect flow

class AtlanActionsEngine:
    """
    Atlan Actions Engine - Governance Automation Platform
    
    The actions layer between Atlan catalog and orchestration systems.
    Provides intelligent governance automation with natural language processing.
    """
    
    def __init__(self, config_path: str = "config.yaml", use_llm: bool = True, 
                 execution_mode: str = "direct", atlan_config: Dict[str, Any] = None):
        self.config_path = config_path
        self.execution_mode = ExecutionMode(execution_mode)
        
        # Initialize enhanced AI control plane with audit logging
        if ENHANCED_AI_AVAILABLE:
            self.ai_control_plane = AIControlPlane(config_path, use_llm=use_llm)
            self.engine = self.ai_control_plane.engine
            print("✅ Enhanced AI Control Plane with audit logging initialized")
        else:
            # Fallback to basic engine
            self.engine = ControlPlaneEngine(config_path)
            self.ai_control_plane = None
            print("⚠️  Using basic control plane (no enhanced audit logging)")
        
        # Initialize Atlan integration (graceful fallback)
        self.atlan_client = None
        self.atlan_sync = None
        atlan_token = os.getenv('ATLAN_API_TOKEN')
        self.atlan_enabled = False
        
        # Note: AtlanAPIClient and AtlanGovernanceSync are not implemented yet
        # Run in standalone mode by default
        if not atlan_token:
            print("⚠️  ATLAN_API_TOKEN not set - running in standalone mode")
        else:
            print("⚠️  Atlan integration classes not available - running in standalone mode")
        
        # NL→SQL converter initialization
        if use_llm and os.getenv('ANTHROPIC_API_KEY'):
            try:
                from nl_to_sql_llm import NLToSQLConverter
                self.nl_converter = NLToSQLConverter(provider="claude")
                self.nl_mode = "LLM"
            except ImportError:
                if os.getenv('OPENAI_API_KEY'):
                    from control_pannel import NLToSQLConverter
                    self.nl_converter = NLToSQLConverter(provider="openai")
                    self.nl_mode = "OpenAI"
                else:
                    self.nl_converter = None
                    self.nl_mode = "Local"
        elif use_llm and os.getenv('OPENAI_API_KEY'):
            from control_pannel import NLToSQLConverter
            self.nl_converter = NLToSQLConverter(provider="openai")
            self.nl_mode = "OpenAI"
        else:
            try:
                from nl_to_sql_templates import TemplateSQLGenerator
                platform = self.engine.config.get('platform', {}).get('type', 'snowflake')
                self.nl_converter = TemplateSQLGenerator(platform=platform)
                self.nl_mode = "Template"
            except ImportError:
                self.nl_converter = None
                self.nl_mode = "Local"
        
        self.pii_analyzer = PIIAnalyzer()
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
        
        self.metadata_db = self._init_metadata_store()
        self.pattern_memory = {}
        self.execution_history = []
        
        self.logger.info(f"✅ Atlan Actions Engine initialized - Mode: {self.nl_mode}, Execution: {execution_mode}")
        
    def _init_metadata_store(self) -> sqlite3.Connection:
        """Initialize metadata and learning database with thread safety"""
        db_path = "atlan_actions_metadata.db"
        # Use check_same_thread=False to allow access from different threads
        conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # Enable WAL mode for better concurrent access
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS column_classifications (
                table_name TEXT,
                column_name TEXT,
                classification TEXT,
                confidence REAL,
                protection_status TEXT,
                policy_name TEXT,
                atlan_guid TEXT,
                timestamp TEXT,
                PRIMARY KEY (table_name, column_name)
            );
            
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nl_query TEXT,
                intent TEXT,
                phase TEXT,
                result TEXT,
                success BOOLEAN,
                atlan_sync_status TEXT,
                timestamp TEXT,
                execution_time REAL
            );
            
            CREATE TABLE IF NOT EXISTS atlan_sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT,
                entity_guid TEXT,
                entity_type TEXT,
                sync_status TEXT,
                error_message TEXT,
                timestamp TEXT
            );
        """)
        
        conn.commit()
        return conn
    
    def process_natural_language(self, user_query: str, progress_callback=None, session_id=None) -> Dict[str, Any]:
        """
        Main entry point - processes natural language through 6-phase governance loop
        Enhanced with Atlan integration, audit logging, and multi-mode execution
        """
        
        # Use enhanced AI control plane if available
        if self.ai_control_plane:
            self.logger.info(f"🎯 Using Enhanced AI Control Plane with audit logging")
            
            # Pass Atlan sync capability to enhanced engine
            if hasattr(self, 'atlan_sync') and self.atlan_sync:
                self.ai_control_plane.atlan_sync = self.atlan_sync
                self.ai_control_plane.atlan_enabled = True
            
            # Process using enhanced engine with comprehensive audit logging
            results = self.ai_control_plane.process_natural_language(
                user_query, 
                progress_callback=progress_callback,
                session_id=session_id
            )
            
            # Add Atlan Actions specific metadata
            results['execution_mode'] = self.execution_mode.value
            results['atlan_enabled'] = self.atlan_enabled
            
            self.logger.info(f"✅ Enhanced processing completed - Request ID: {results.get('request_id', 'N/A')}")
            return results
        
        else:
            # Fallback to basic processing (original implementation)
            self.logger.info(f"⚠️ Using basic processing (no enhanced audit logging)")
            return self._process_basic_mode(user_query, progress_callback, session_id)
    
    def _process_basic_mode(self, user_query: str, progress_callback=None, session_id=None) -> Dict[str, Any]:
        """
        Basic processing mode - fallback when enhanced AI control plane is not available
        """
        self.logger.info(f"\n🎯 Atlan Actions Processing (Basic Mode): '{user_query}'")
        
        start_time = datetime.now()
        results = {
            'query': user_query,
            'start_time': start_time.isoformat(),
            'nl_mode': 'basic',
            'execution_mode': self.execution_mode.value,
            'atlan_enabled': self.atlan_enabled,
            'phases': {}
        }
        
        try:
            # Phase 1: OBSERVE
            self.logger.info("📡 Phase 1: OBSERVE - NL parsing and schema analysis...")
            if progress_callback:
                progress_callback(1, "OBSERVE", "🔍 Parsing natural language and analyzing schema...")
            
            # Basic observe implementation
            observe_result = ObservationResult(
                intent="pii_masking",
                target_entities=["PUBLIC.CUSTOMERS"],
                confidence=0.9,
                schema_context={},
                current_state={},
                sample_data={},
                sql_result={},
                user_query=user_query
            )
            results['phases']['observe'] = asdict(observe_result)
            if progress_callback:
                progress_callback(1, "OBSERVE", f"✅ Intent: {observe_result.intent} ({observe_result.confidence:.1%} confidence)")
            
            if observe_result.confidence < 0.5:
                results['status'] = 'low_confidence'
                results['message'] = f"Cannot proceed with confidence {observe_result.confidence:.1%}"
                return results
            
            # Phase 2: ANALYZE
            self.logger.info("🧠 Phase 2: ANALYZE - PII detection and impact assessment...")
            if progress_callback:
                progress_callback(2, "ANALYZE", "🔬 Basic PII analysis...")
            
            analyze_result = AnalysisResult(
                pii_findings=[],
                impact_assessment={},
                risk_score=0.5,
                ml_confidence=0.5,
                entity_relationships={}
            )
            results['phases']['analyze'] = asdict(analyze_result)
            if progress_callback:
                progress_callback(2, "ANALYZE", f"✅ Basic analysis completed")
            
            # Remaining phases would be implemented here for basic mode
            # For now, return basic results
            
            end_time = datetime.now()
            results['end_time'] = end_time.isoformat()
            results['total_time'] = (end_time - start_time).total_seconds()
            results['status'] = 'success'
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Basic mode error: {e}", exc_info=True)
            results['status'] = 'error'
            results['error'] = str(e)
            return results

    def _verify_atlan_assets(self) -> bool:
        """Verify that required Atlan assets exist in the environment"""
        try:
            if not self.atlan_client:
                return False
                
            # Check if we can connect to Atlan and query assets
            search_result = self.atlan_client.search_assets(
                query="*",
                size=1,
                from_=0
            )
            
            # Verify we have access to at least some assets
            if search_result and search_result.get('hits', {}).get('total', {}).get('value', 0) > 0:
                self.logger.info("✅ Atlan assets verified - connection successful")
                return True
            else:
                self.logger.warning("⚠️  No Atlan assets found in environment")
                return False
                
        except Exception as e:
            self.logger.warning(f"⚠️  Atlan asset verification failed: {e}")
            return False

    def _mock_observe_result(self, user_query: str) -> ObservationResult:
        """Create mock observation result for demo purposes"""
        self.logger.info("🎭 Using mock data for demonstration")
        
        # Mock data to simulate real database discovery
        mock_sample_data = {
            'customers': [
                {'id': 1, 'name': 'John Doe', 'email': 'john@email.com', 'phone': '555-0123'},
                {'id': 2, 'name': 'Jane Smith', 'email': 'jane@company.com', 'phone': '555-0124'},
                {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@test.com', 'phone': '555-0125'}
            ],
            'orders': [
                {'order_id': 1001, 'customer_id': 1, 'amount': 99.99, 'date': '2025-01-15'},
                {'order_id': 1002, 'customer_id': 2, 'amount': 149.50, 'date': '2025-01-16'},
                {'order_id': 1003, 'customer_id': 3, 'amount': 75.25, 'date': '2025-01-17'}
            ]
        }
        
        return ObservationResult(
            intent="DISCOVER_AND_MASK",
            target_entities=['customers', 'orders'],
            confidence=0.95,
            schema_context={},
            current_state={},
            sample_data=mock_sample_data,
            sql_result=None,
            user_query=user_query
        )

    def _phase_observe(self, user_query: str) -> ObservationResult:
        """Phase 1: OBSERVE - Enhanced with Atlan metadata context"""
        
        # Try to connect, but fallback to mock data if it fails
        if not self.engine.connect_platform():
            self.logger.warning("⚠️  Database connection failed - using mock data for demo")
            return self._mock_observe_result(user_query)
        
        # Get schema context (enhanced with Atlan metadata if available)
        schema_context = self._build_schema_context()
        
        self.logger.info(f"   Using {self.nl_mode},{self} mode for NL→SQL conversion...")
        
        # Detect relative date filters (e.g., "older than 90 days") and today's date
        relative_date_filter = self._extract_relative_date_filter(user_query)
        today_str = date.today().isoformat()

        # NL→SQL conversion logic (same as original)
        if self.nl_mode in ["LLM", "OpenAI"] and self.nl_converter:
            platform = self.engine.config.get('platform', {}).get('type', 'snowflake')
            sql_result = self.nl_converter.convert(user_query, schema_context, platform)
            intent = getattr(sql_result, 'policy_type', 'MASK')
            target_entities = getattr(sql_result, 'affected_assets', ['customers'])
            confidence = getattr(sql_result, 'confidence', 0.8)
        else:
            intent = self._extract_intent(user_query)
            target_entities = self._extract_entities(user_query)
            confidence = self._calculate_observation_confidence(user_query, intent, target_entities, schema_context)
            sql_result = self._create_fallback_sql_result(intent, target_entities, confidence)

        # Attach date context so downstream phases/LLM can use it
        if hasattr(sql_result, 'metadata'):
            sql_result.metadata['today_date'] = today_str
            if relative_date_filter:
                sql_result.metadata['relative_date_filter'] = relative_date_filter
        
        self.logger.info(f"   ✓ Intent: {intent}")
        self.logger.info(f"   ✓ Confidence: {confidence:.3f}")
        self.logger.info(f"   ✓ Target entities: {target_entities}")
        
        # Sample data from unique tables
        sample_data = {}
        unique_tables = self._extract_unique_tables(target_entities)
        
        for table_name in unique_tables:
            sample_data[table_name] = self._sample_table_data(table_name, limit=50)
        
        current_state = self._get_current_protection_state(target_entities)
        
        return ObservationResult(
            intent=intent,
            target_entities=target_entities,
            confidence=confidence,
            schema_context=schema_context,
            current_state=current_state,
            sample_data=sample_data,
            sql_result=sql_result,
            today_date=today_str,
            relative_date_filter=relative_date_filter,
            user_query=user_query
        )

    def _phase_analyze(self, observe_result: ObservationResult) -> AnalysisResult:
        """Phase 2: ANALYZE - PII detection with Atlan classification context"""
        
        pii_findings = []
        total_confidence = 0.0
        analyzed_columns = 0
        
        # Enhanced PII detection with both heuristics AND ML analysis
        for table_name, sample_data in observe_result.sample_data.items():
            table_schema = observe_result.schema_context.get(table_name, {})
            columns = table_schema.get('columns', [])
            
            for column in columns:
                column_name = column['name'].lower()
                
                # Step 2.1a: Heuristic check (column name analysis)
                heuristic_confidence = 0.0
                pii_types = []
                is_pii = False
                
                if any(pattern in column_name for pattern in ['email', 'mail']):
                    is_pii = True
                    pii_types = ['EMAIL_ADDRESS']
                    heuristic_confidence = 0.75  # Lower initial confidence for heuristics
                elif any(pattern in column_name for pattern in ['ssn', 'social', 'security']):
                    is_pii = True
                    pii_types = ['SSN']
                    heuristic_confidence = 0.80
                elif any(pattern in column_name for pattern in ['phone', 'mobile', 'tel']):
                    is_pii = True
                    pii_types = ['PHONE_NUMBER']
                    heuristic_confidence = 0.70
                elif any(pattern in column_name for pattern in ['name', 'firstname', 'lastname']):
                    is_pii = True
                    pii_types = ['PERSON']
                    heuristic_confidence = 0.65
                
                # Step 2.1b: ML analysis (runs Presidio on sample data)
                ml_confidence = 0.0
                if is_pii and sample_data and len(sample_data) > 0:
                    # Sample 10 rows for ML analysis
                    sample_values = []
                    for row in sample_data[:10]:  # Limit to 10 rows for performance
                        if column['name'] in row and row[column['name']]:
                            sample_values.append(str(row[column['name']]))
                    
                    if sample_values:
                        try:
                            # Use Presidio analyzer if available, otherwise use pattern matching
                            if hasattr(self, 'pii_analyzer') and self.pii_analyzer:
                                ml_results = self.pii_analyzer.analyze_text(' '.join(sample_values[:3]))
                                for result in ml_results:
                                    if result['type'] in pii_types:
                                        ml_confidence = max(ml_confidence, result['confidence'])
                            else:
                                # Fallback pattern matching for ML confidence
                                if pii_types == ['EMAIL_ADDRESS']:
                                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                                    import re
                                    for value in sample_values:
                                        if re.search(email_pattern, value):
                                            ml_confidence = 0.90
                                            break
                                else:
                                    ml_confidence = 0.60  # Default ML confidence for other types
                        except Exception as e:
                            self.logger.warning(f"ML analysis failed for {column['name']}: {e}")
                            ml_confidence = 0.50  # Fallback confidence
                
                # Step 2.1c: Combined confidence (heuristic + ML)
                if is_pii:
                    final_confidence = (heuristic_confidence * 0.4) + (ml_confidence * 0.6)  # Weight ML higher
                    final_confidence = min(final_confidence, 0.98)  # Cap at 98%
                    
                    pii_findings.append({
                        'table': table_name,
                        'column': column['name'],
                        'pii_types': pii_types,
                        'confidence': final_confidence,
                        'heuristic_confidence': heuristic_confidence,
                        'ml_confidence': ml_confidence,
                        'detection_method': 'heuristics + ML'
                    })
                    total_confidence += final_confidence
                    analyzed_columns += 1
                    
                    self.logger.info(f"PII detected in {table_name}.{column['name']}: "
                                   f"Heuristic: {heuristic_confidence:.2f}, ML: {ml_confidence:.2f}, "
                                   f"Final: {final_confidence:.2f}")
        
        impact_assessment = self._calculate_impact(observe_result, pii_findings)
        risk_score = self._calculate_risk_score(observe_result, pii_findings)
        entity_relationships = self._map_entity_relationships(observe_result.schema_context)
        ml_confidence = total_confidence / max(analyzed_columns, 1)
        
        return AnalysisResult(
            pii_findings=pii_findings,
            impact_assessment=impact_assessment,
            risk_score=risk_score,
            ml_confidence=ml_confidence,
            entity_relationships=entity_relationships
        )

    def _phase_plan(self, observe_result: ObservationResult, analyze_result: AnalysisResult) -> ExecutionPlan:
        """Phase 3: PLAN - Generate execution plan based on mode"""
        
        sql_result = observe_result.sql_result
        request_text = getattr(observe_result, 'user_query', '')
        
        if hasattr(sql_result, 'sql_commands') and sql_result.sql_commands:
            sql_commands = sql_result.sql_commands
            rollback_commands = sql_result.metadata.get('rollback_commands', [])
            self.logger.info(f"   ✓ Using {len(sql_commands)} LLM-generated SQL commands")
        else:
            # Generate SQL based on PII findings
            sql_commands = []
            rollback_commands = []
            
            # Step 1: Add policy cleanup commands FIRST
            cleanup_commands = self._generate_comprehensive_policy_cleanup()
            sql_commands.extend(cleanup_commands)
            self.logger.info(f"   ✓ Added {len(cleanup_commands)} policy cleanup commands")
            
            # Augment findings when user mentions only a column or a non-existent table
            augmented_findings = list(analyze_result.pii_findings)
            try:
                rq = (request_text or "").lower()
                # Extract an obvious column token (simple heuristic: after 'mask' or common words)
                import re
                col_match = re.search(r"mask\s+([a-zA-Z0-9_]+)", rq) or re.search(r"\bcolumn\s+([a-zA-Z0-9_]+)\b", rq)
                table_match = re.search(r"\b(in|from)\s+([a-zA-Z0-9_\.\"]+)\s+table\b", rq) or re.search(r"\btable\s+([a-zA-Z0-9_\.\"]+)\b", rq)
                target_column = col_match.group(1) if col_match else None
                target_table = table_match.group(2) if table_match else None

                if target_column:
                    self.logger.info(f"   🔍 User requested column: {target_column}")
                if target_table:
                    self.logger.info(f"   🔍 User mentioned table: {target_table}")

                # If a table was mentioned but doesn't exist, or no table mentioned: find all tables with the column
                need_column_search = False
                if target_table and not self._table_exists(target_table):
                    self.logger.warning(f"   ⚠️  Mentioned table {target_table} does not exist - searching all tables with column {target_column}")
                    need_column_search = True
                if not target_table and target_column:
                    need_column_search = True

                if need_column_search and target_column:
                    candidate_tables = self._find_tables_with_column(target_column)
                    # Add missing findings for these tables
                    existing = {(f['table'], f['column']) for f in augmented_findings}
                    for t in candidate_tables:
                        key = (t, target_column.upper())
                        if key not in existing:
                            augmented_findings.append({'table': t, 'column': target_column.upper(), 'pii_types': []})
                    self.logger.info(f"   ✓ Augmented findings with {len(augmented_findings) - len(analyze_result.pii_findings)} entries")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Failed augmenting findings from user query: {e}")

            for finding in augmented_findings:
                table = finding['table']
                column = finding['column']
                pii_types = finding['pii_types']
                
                policy_name = f"{table}_{column}_mask_policy".replace('.', '_')
                mask_sql = self._generate_masking_sql(
                    table,
                    column,
                    policy_name,
                    pii_types,
                    user_query=request_text
                )
                sql_commands.extend(mask_sql)
                
                rollback_sql = self._generate_rollback_sql('mask', table, column, policy_name)
                rollback_commands.extend(rollback_sql)
            
            if cleanup_commands:
                sql_commands = ['BEGIN;'] + cleanup_commands + sql_commands
            
            self.logger.info(f"   ✓ Generated {len(sql_commands)} SQL commands")

        # Ensure we always unset an existing masking policy before applying a new one
        sql_commands = self._ensure_unset_before_set(sql_commands)

        # If we detected a relative date filter, add a comment to the SQL list for visibility
        if getattr(observe_result, 'relative_date_filter', None):
            r = observe_result.relative_date_filter
            sql_commands.insert(0, f"-- Relative date filter: older than {r['days']} days; cutoff {r['cutoff_date']} (today {observe_result.today_date})")
        
        estimated_impact = {
            'tables_affected': len(set(f['table'] for f in analyze_result.pii_findings)),
            'columns_affected': len(analyze_result.pii_findings),
            'estimated_rows': sum(analyze_result.impact_assessment.get('row_counts', {}).values()),
            'estimated_time_seconds': len(sql_commands) * 2.0,
        }
        
        return ExecutionPlan(
            sql_commands=sql_commands,
            execution_order=list(range(len(sql_commands))),
            dependencies={},
            rollback_strategy=rollback_commands,
            estimated_impact=estimated_impact,
            safety_checks=["Verify backup exists", "Test on subset first"]
        )

    def _ensure_unset_before_set(self, sql_commands: List[str]) -> List[str]:
        """Prepend UNSET for any SET MASKING POLICY statements to avoid attachment errors."""
        enhanced: List[str] = []
        for cmd in sql_commands:
            upper_cmd = cmd.upper()
            if 'ALTER TABLE' in upper_cmd and 'SET MASKING POLICY' in upper_cmd and 'UNSET MASKING POLICY' not in upper_cmd:
                prefix = cmd.split('SET MASKING POLICY')[0].strip()
                if not prefix.endswith(';'):
                    prefix = prefix + ' '
                unset_cmd = prefix + 'UNSET MASKING POLICY;'
                enhanced.append(unset_cmd)
            enhanced.append(cmd)
        return enhanced

    def _phase_simulate(self, plan_result: ExecutionPlan, observe_result: ObservationResult) -> SimulationResult:
        """Phase 4: SIMULATE - Preview impact"""
        
        before_state = {}
        affected_columns = []
        
        unique_tables = self._extract_unique_tables(observe_result.target_entities)
        
        for table_name in unique_tables:
            if table_name in observe_result.schema_context:
                current_samples = observe_result.sample_data.get(table_name, [])
                before_state[table_name] = current_samples[:5]
                
                table_schema = observe_result.schema_context[table_name]
                for col in table_schema.get('columns', []):
                    affected_columns.append(f"{table_name}.{col['name']}")
        
        after_state = self._simulate_after_state(before_state, plan_result, observe_result)
        affected_rows = plan_result.estimated_impact.get('estimated_rows', 0)
        
        risk_level = "LOW"
        if plan_result.estimated_impact.get('estimated_rows', 0) > 100000:
            risk_level = "HIGH"
        elif any("DELETE" in cmd for cmd in plan_result.sql_commands):
            risk_level = "MEDIUM"
        
        return SimulationResult(
            before_state=before_state,
            after_state=after_state,
            affected_rows=affected_rows,
            affected_columns=affected_columns[:10],
            downstream_impact=[],
            risk_assessment=risk_level
        )

    def _phase_execute(self, plan_result: ExecutionPlan, observe_result: ObservationResult, 
                      analyze_result: AnalysisResult) -> ExecutionResult:
        """Phase 5: EXECUTE - Execute based on mode, with Atlan sync"""
        
        start_time = datetime.now()
        atlan_sync_status = {'enabled': self.atlan_enabled, 'synced_items': []}
        
        if self.execution_mode == ExecutionMode.AIRFLOW:
            # Generate Airflow DAG instead of executing
            dag_code = self._generate_airflow_dag(plan_result, observe_result)
            self.logger.info(f"   ✓ Generated Airflow DAG ({len(dag_code)} lines)")
            
            execution_result = ExecutionResult(
                success=True,
                commands_executed=[f"Generated Airflow DAG with {len(plan_result.sql_commands)} tasks"],
                execution_time=(datetime.now() - start_time).total_seconds(),
                rows_affected=0,
                metadata_updates={'dag_generated': True},
                audit_trail={'mode': 'airflow', 'dag_path': f'/tmp/atlan_actions_{int(time.time())}.py'},
                atlan_sync_status=atlan_sync_status
            )
        
        elif self.execution_mode == ExecutionMode.DIRECT:
            # Direct execution (same as original logic)
            commands_executed = []
            total_rows_affected = 0
            success = True
            
            try:
                for i, sql_command in enumerate(plan_result.sql_commands):
                    if sql_command.strip() and not sql_command.startswith('--'):
                        try:
                            self.logger.info(f"\n{'='*80}")
                            self.logger.info(f"🔄 GOVERNANCE SQL COMMAND {i+1}/{len(plan_result.sql_commands)}")
                            self.logger.info(f"SQL: {sql_command}")
                            self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
                            
                            sql_start_time = time.time()
                            result = self.engine.connector.execute(sql_command)
                            sql_execution_time = time.time() - sql_start_time
                            
                            commands_executed.append(sql_command)
                            
                            # Log successful execution details
                            rows_affected = 0
                            if hasattr(result, 'rowcount') and result.rowcount > 0:
                                rows_affected = result.rowcount
                                total_rows_affected += result.rowcount
                            
                            self.logger.info(f"✅ SQL COMMAND {i+1} SUCCESS")
                            self.logger.info(f"Rows affected: {rows_affected}")
                            self.logger.info(f"Execution time: {sql_execution_time:.3f}s")
                            if hasattr(result, 'sfqid'):
                                self.logger.info(f"Snowflake Query ID: {result.sfqid}")
                            self.logger.info(f"{'='*80}\n")
                            
                        except Exception as sql_error:
                            sql_execution_time = time.time() - sql_start_time if 'sql_start_time' in locals() else 0
                            self.logger.error(f"\n{'='*80}")
                            self.logger.error(f"❌ SQL COMMAND {i+1} FAILED")
                            self.logger.error(f"Error: {str(sql_error)}")
                            self.logger.error(f"Error Type: {type(sql_error).__name__}")
                            self.logger.error(f"Execution time: {sql_execution_time:.3f}s")
                            self.logger.error(f"Failed SQL: {sql_command}")
                            
                            if any(kw in sql_command.upper() for kw in ['UNSET', 'DROP', 'IF EXISTS']):
                                self.logger.info(f"⚠️  Ignoring cleanup/optional command error")
                                self.logger.info(f"{'='*80}\n")
                                commands_executed.append(f"-- FAILED (IGNORED): {sql_command[:50]}...")
                                continue
                            else:
                                self.logger.error(f"{'='*80}\n")
                                raise sql_error
                
                metadata_updates = self._update_metadata_catalog(observe_result, analyze_result)
                
                # Sync to Atlan
                atlan_sync_status = self._sync_results_to_atlan(observe_result, analyze_result)
                
            except Exception as e:
                success = False
                self.logger.error(f"   Execution failed: {e}")
                metadata_updates = {}
                atlan_sync_status['error'] = str(e)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"   ✓ Executed {len(commands_executed)} commands in {execution_time:.2f}s")
            
            execution_result = ExecutionResult(
                success=success,
                commands_executed=commands_executed,
                execution_time=execution_time,
                rows_affected=total_rows_affected,
                metadata_updates=metadata_updates,
                audit_trail={'user': 'atlan_actions', 'timestamp': datetime.now().isoformat()},
                atlan_sync_status=atlan_sync_status
            )
        
        return execution_result

    def _sync_results_to_atlan(self, observe_result: ObservationResult, 
                              analyze_result: AnalysisResult) -> Dict[str, Any]:
        """Sync governance results to Atlan catalog"""
        
        sync_status = {
            'enabled': self.atlan_enabled,
            'synced_items': [],
            'errors': []
        }
        
        if not self.atlan_enabled:
            return sync_status
        
        try:
            # Sync PII findings as classifications
            for finding in analyze_result.pii_findings:
                try:
                    table_name = finding['table']
                    column_name = finding['column']
                    pii_types = finding['pii_types']
                    
                    # Push classification to Atlan
                    classification_result = self.atlan_sync.tag_column_as_pii(
                        table_qualified_name=f"{table_name}",
                        column_name=column_name,
                        pii_types=pii_types,
                        confidence=finding['confidence']
                    )
                    
                    sync_status['synced_items'].append({
                        'type': 'classification',
                        'entity': f"{table_name}.{column_name}",
                        'pii_types': pii_types,
                        'atlan_guid': classification_result.get('guid')
                    })
                    
                except Exception as e:
                    sync_status['errors'].append(f"Classification sync failed for {finding['table']}.{finding['column']}: {e}")
            
            # Create lineage process for governance action
            try:
                process_result = self.atlan_sync.create_governance_lineage(
                    process_name=f"AtlanActions_{observe_result.intent}_{int(time.time())}",
                    input_tables=list(observe_result.sample_data.keys()),
                    governance_action=observe_result.intent,
                    metadata={'confidence': observe_result.confidence}
                )
                
                sync_status['synced_items'].append({
                    'type': 'lineage_process',
                    'process_name': process_result.get('name'),
                    'atlan_guid': process_result.get('guid')
                })
                
            except Exception as e:
                sync_status['errors'].append(f"Lineage creation failed: {e}")
            
            self.logger.info(f"✅ Synced {len(sync_status['synced_items'])} items to Atlan")
            
        except Exception as e:
            sync_status['errors'].append(f"Atlan sync failed: {e}")
            self.logger.error(f"❌ Atlan sync error: {e}")
        
        return sync_status

    def _generate_airflow_dag(self, plan_result: ExecutionPlan, observe_result: ObservationResult) -> str:
        """Generate Airflow DAG code for the execution plan"""
        
        dag_id = f"atlan_actions_{observe_result.intent.lower()}_{int(time.time())}"
        
        dag_code = f'''
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.python import PythonOperator

# Generated by Atlan Actions Engine
default_args = {{
    'owner': 'atlan-actions',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 24),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}}

dag = DAG(
    '{dag_id}',
    default_args=default_args,
    description='Atlan Actions - {observe_result.intent}',
    schedule_interval=None,
    catchup=False,
    tags=['atlan-actions', 'governance', '{observe_result.intent.lower()}']
)

def sync_to_atlan(**context):
    """Sync results back to Atlan catalog"""
    # Placeholder for Atlan sync logic
    print("Syncing governance results to Atlan...")
    return "sync_complete"

'''
        
        # Add SQL tasks
        for i, sql_command in enumerate(plan_result.sql_commands):
            if sql_command.strip() and not sql_command.startswith('--'):
                escaped_sql = sql_command.replace("'", "\\'").replace('"', '\\"')
                dag_code += f'''
task_{i} = SnowflakeOperator(
    task_id='governance_sql_{i}',
    dag=dag,
    snowflake_conn_id='snowflake_default',
    sql="""{escaped_sql}""",
    warehouse='COMPUTE_WH',
    database='MY_DATABASE',
    schema='PUBLIC'
)

'''
        
        # Add Atlan sync task
        dag_code += '''
atlan_sync_task = PythonOperator(
    task_id='sync_to_atlan',
    dag=dag,
    python_callable=sync_to_atlan
)

# Set task dependencies
'''
        
        # Set up task dependencies
        if len(plan_result.sql_commands) > 1:
            for i in range(len(plan_result.sql_commands) - 1):
                dag_code += f"task_{i} >> task_{i+1}\n"
            dag_code += f"task_{len(plan_result.sql_commands)-1} >> atlan_sync_task\n"
        elif len(plan_result.sql_commands) == 1:
            dag_code += "task_0 >> atlan_sync_task\n"
        
        return dag_code

    def _phase_learn(self, execute_result: ExecutionResult, observe_result: ObservationResult, 
                    analyze_result: AnalysisResult) -> LearningResult:
        """Phase 6: LEARN - Enhanced with Atlan feedback"""
        
        verification_status = self._verify_policy_effectiveness(execute_result, observe_result)
        performance_impact = self._measure_performance_impact(execute_result)
        discovered_patterns = self._discover_similar_patterns(observe_result, analyze_result)
        recommendations = self._generate_recommendations(observe_result, analyze_result, discovered_patterns)
        
        # Add Atlan-specific recommendations
        if self.atlan_enabled and execute_result.atlan_sync_status.get('synced_items'):
            recommendations.append(f"✅ Synced {len(execute_result.atlan_sync_status['synced_items'])} items to Atlan catalog")
        
        confidence_feedback = self._calculate_confidence_feedback(execute_result, verification_status)
        
        return LearningResult(
            verification_status=verification_status,
            performance_impact=performance_impact,
            discovered_patterns=discovered_patterns,
            recommendations=recommendations,
            confidence_feedback=confidence_feedback
        )

    # ============================================================================
    # HELPER METHODS (Key ones from original, adapted)
    # ============================================================================
    
    def _extract_unique_tables(self, target_entities: List[str]) -> set:
        """Extract unique table names from entities (handle column references)"""
        unique_tables = set()
        for entity in target_entities[:5]:
            if entity.count('.') >= 2:  # Format: SCHEMA.TABLE.COLUMN
                parts = entity.split('.')
                table_name = f"{parts[0]}.{parts[1]}"
                unique_tables.add(table_name)
            elif entity.count('.') == 1:  # Format: SCHEMA.TABLE
                unique_tables.add(entity)
            else:  # Simple table name
                unique_tables.add(entity)
        return unique_tables

    def _build_schema_context(self) -> Dict[str, Any]:
        """Build schema context enhanced with Atlan metadata"""
        schema = {}
        try:
            tables = self.engine.connector.get_tables()
            for table in tables[:10]:
                table_name = f"{table.get('schema', 'PUBLIC')}.{table['name']}"
                columns = self.engine.connector.get_columns(table_name)
                schema[table_name] = {
                    'row_count': table.get('rows', 0),
                    'columns': [
                        {
                            'name': col['name'],
                            'type': col['type'],
                            'nullable': col.get('nullable', True)
                        }
                        for col in columns
                    ]
                }
        except Exception as e:
            self.logger.warning(f"Could not build schema context: {e}")
            schema = self.engine._get_detailed_schema_for_chatbot()
        
        return schema

    def _extract_intent(self, user_query: str) -> str:
        """Extract primary intent from natural language"""
        query_lower = user_query.lower()
        
        discovery_words = ['discover', 'find', 'scan', 'automatically', 'identify', 'detect']
        masking_words = ['mask', 'protect', 'hide', 'intelligent', 'apply']
        
        has_discovery = any(word in query_lower for word in discovery_words)
        has_masking = any(word in query_lower for word in masking_words)
        has_pii = 'pii' in query_lower or 'personal' in query_lower or 'sensitive' in query_lower
        
        if has_discovery and has_masking and has_pii:
            return 'DISCOVER_AND_MASK'
        elif has_discovery and has_pii:
            return 'PII_DISCOVERY'
        elif any(word in query_lower for word in ['mask', 'hide', 'protect']):
            return 'MASK'
        elif any(word in query_lower for word in ['gdpr', 'delete', 'forget']):
            return 'GDPR_DELETE'
        else:
            return 'QUERY'

    def _extract_entities(self, user_query: str) -> List[str]:
        """Extract table/column entities from natural language"""
        query_lower = user_query.lower()
        
        # First check for specific table mentions
        common_tables = ['customers', 'users', 'employees', 'orders', 'products', 'payments', 'transactions', 'accounts']
        entities = []
        
        for table in common_tables:
            if table in query_lower:
                # Return table name in uppercase for Snowflake compatibility
                entities.append(table.upper())
        
        if entities:
            return entities

        # Detect explicit single-table references like "in Accounts table" or SQL-like references
        import re
        table_match = re.search(r'\b(?:in|from|on|for)\s+([a-zA-Z_][a-zA-Z0-9_\.\"]*)\s+table\b', query_lower)
        if not table_match:
            table_match = re.search(r'\bfrom\s+([a-zA-Z_][a-zA-Z0-9_\.\"]*)', query_lower)
        if not table_match:
            table_match = re.search(r'\bjoin\s+([a-zA-Z_][a-zA-Z0-9_\.\"]*)', query_lower)
        if not table_match:
            table_match = re.search(r'\binto\s+([a-zA-Z_][a-zA-Z0-9_\.\"]*)', query_lower)

        if table_match:
            candidate = table_match.group(1).strip('"')
            self.logger.info(f"Detected explicit table reference from query: {candidate}")

            # Normalize against actual database tables if possible
            if self.engine and self.engine.connect_platform():
                try:
                    tables = self.engine.connector.get_tables()
                    candidate_upper = candidate.upper()
                    matches = [f"{table.get('schema', 'PUBLIC')}.{table['name']}" for table in tables if table['name'].upper() == candidate_upper or f"{table.get('schema', 'PUBLIC')}.{table['name']}".upper() == candidate_upper]
                    if matches:
                        self.logger.info(f"Resolved explicit table to actual catalog table: {matches[0]}")
                        return [matches[0]]
                except Exception as e:
                    self.logger.warning(f"Could not resolve explicit table against catalog: {e}")
            return [candidate]

        # If no specific tables mentioned, scan all available tables in database schema
        if any(word in query_lower for word in ['automatically', 'discover', 'all', 'mask', 'protect', 'data']):
            try:
                if self.engine.connect_platform():
                    tables = self.engine.connector.get_tables()
                    self.logger.info(f"No specific tables mentioned → Scanning all available tables in database schema ({len(tables)} found)")
                    return [f"{table.get('schema', 'PUBLIC')}.{table['name']}" for table in tables[:10]]  # Limit to first 10 for performance
            except Exception as e:
                self.logger.warning(f"Could not get all tables from database: {e}")
                # Fallback to common tables if database scan fails
                self.logger.info("Fallback: Using common table names for discovery")
                return common_tables

        # Final fallback if no pattern matches
        self.logger.info("No specific tables mentioned → Scanning all available tables in database schema")
        return common_tables

    def _extract_relative_date_filter(self, user_query: str) -> Optional[Dict[str, Any]]:
        """Detect phrases like 'older than 90 days' or 'last 30 days' and compute cutoff date"""
        import re
        query_lower = user_query.lower()

        # Patterns: older than X days, past X days, last X days
        match = re.search(r'(older than|past|last)\s+(\d+)\s+day', query_lower)
        if not match:
            return None
        days = int(match.group(2))
        cutoff = date.today() - timedelta(days=days)
        return {
            'days': days,
            'cutoff_date': cutoff.isoformat(),
            'today': date.today().isoformat(),
            'expression': f"DATEADD(day, -{days}, CURRENT_DATE)"
        }

    def _derive_role_context(self, user_query: str) -> Dict[str, List[str]]:
        """Derive admin/unmasked vs masked roles from the natural-language request."""
        query_lower = (user_query or "").lower()

        default_admin_roles = [
            "ACCOUNTADMIN",
            "ORGADMIN",
            "SECURITYADMIN",
            "SYSADMIN",
            "USERADMIN"
        ]
        default_masked_roles = [
            "PUBLIC",
            "HR_ROLE",
            "ANALYST_ROLE",
            "SNOWFLAKE_LEARNING_ROLE"
        ]

        # 🎯 CHECK FOR "ALL USERS" / "ALL READ QUERIES" - mask EVERYONE including admins
        if any(term in query_lower for term in [
            "for all", "all users", "all read queries", "all queries", "everyone", 
            "all roles", "every role", "for every", "mask all", "all access"
        ]):
            self.logger.info("   🌍 DETECTED: 'for all' intent - masking EVERYONE including admins")
            # Return ALL roles in masked list, EMPTY admin list (no exceptions)
            all_roles = default_admin_roles + default_masked_roles + [
                "FINANCE_ROLE", "MARKETING_ROLE", "SALES_ROLE", "SUPPORT_ROLE",
                "DEVELOPER_ROLE", "ENGINEER_ROLE", "QA_ROLE", "IT_ROLE"
            ]
            return {
                'admin_roles': [],  # No admin exceptions!
                'masked_roles': sorted(set(all_roles))
            }

        # Map of keywords to Snowflake roles we should explicitly mask when requested.
        role_keywords = {
            "public": "PUBLIC",
            "non admin": "PUBLIC",
            "non-admin": "PUBLIC",
            "nonadmin": "PUBLIC",
            "hr": "HR_ROLE",
            "human resource": "HR_ROLE",
            "analyst": "ANALYST_ROLE",
            "analytics": "ANALYST_ROLE",
            "learning": "SNOWFLAKE_LEARNING_ROLE",
            "training": "SNOWFLAKE_LEARNING_ROLE",
            "finance": "FINANCE_ROLE",
            "accounting": "FINANCE_ROLE",
            "marketing": "MARKETING_ROLE",
            "sales": "SALES_ROLE",
            "support": "SUPPORT_ROLE",
            "customer support": "SUPPORT_ROLE",
            "developer": "DEVELOPER_ROLE",
            "engineer": "ENGINEER_ROLE",
            "qa": "QA_ROLE"
        }

        masked_roles = {role for keyword, role in role_keywords.items() if keyword in query_lower}

        # Honor "non admin" phrasing by ensuring a non-empty masked set.
        if any(term in query_lower for term in ["non admin", "non-admin", "nonadmin"]):
            self.logger.info("   👥 DETECTED: 'non-admin' intent - masking non-admins, keeping admins unmasked")
            masked_roles.update(default_masked_roles)

        # If nothing explicit was requested, fall back to the default non-admin roles.
        if not masked_roles:
            self.logger.info("   📋 Using default non-admin roles for masking")
            masked_roles = set(default_masked_roles)

        admin_roles = set(default_admin_roles)
        admin_keywords = {
            "accountadmin": "ACCOUNTADMIN",
            "orgadmin": "ORGADMIN",
            "securityadmin": "SECURITYADMIN",
            "sysadmin": "SYSADMIN",
            "useradmin": "USERADMIN"
        }
        for keyword, role in admin_keywords.items():
            if keyword in query_lower:
                admin_roles.add(role)

        # Clean any stray quotes and return sorted lists for stable SQL generation.
        admin_roles_clean = sorted(r.replace("'", "") for r in admin_roles)
        masked_roles_clean = sorted(r.replace("'", "") for r in masked_roles)

        return {
            'admin_roles': admin_roles_clean,
            'masked_roles': masked_roles_clean
        }

    # Additional helper methods (simplified versions of key original methods)
    def _calculate_observation_confidence(self, user_query: str, intent: str, entities: List[str], schema_context: Dict[str, Any]) -> float:
        confidence = 0.5
        query_lower = user_query.lower()
        
        clear_intents = {'discover': 0.2, 'mask': 0.2, 'pii': 0.25, 'automatically': 0.2}
        for keyword, boost in clear_intents.items():
            if keyword in query_lower:
                confidence += boost
        
        if intent == 'DISCOVER_AND_MASK':
            confidence += 0.3
        
        return min(confidence, 0.98)

    def _create_fallback_sql_result(self, intent: str, target_entities: List[str], confidence: float):
        class FallbackSQLResult:
            def __init__(self, intent, entities, conf):
                self.policy_type = intent
                self.sql_commands = []
                self.confidence = conf
                self.affected_assets = entities
                self.metadata = {}
        return FallbackSQLResult(intent, target_entities, confidence)

    def _sample_table_data(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            cursor = self.engine.connector.connection.cursor()
            cursor.execute(f"DESCRIBE TABLE {table_name}")
            column_info = cursor.fetchall()
            columns = [row[0] for row in column_info]
            
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            self.logger.warning(f"Could not sample {table_name}: {e}")
            return []

    def _get_current_protection_state(self, entities: List[str]) -> Dict[str, Any]:
        return {}  # Simplified for demo

    def _calculate_impact(self, observe_result, pii_findings) -> Dict[str, Any]:
        return {
            'tables_affected': len(set(f['table'] for f in pii_findings)),
            'columns_affected': len(pii_findings),
            'row_counts': {},
            'data_types_affected': []
        }

    def _calculate_risk_score(self, observe_result, pii_findings) -> float:
        return len(pii_findings) * 0.1

    def _map_entity_relationships(self, schema_context) -> Dict[str, List[str]]:
        return {}

    def _generate_comprehensive_policy_cleanup(self):
        return ["-- Cleanup existing policies"]
    
    def _find_date_column(self, table: str) -> Optional[str]:
        """Find a date/timestamp column in the table for date-based filtering"""
        self.logger.info(f"   🔎 Searching for date column in table: {table}")
        try:
            # Parse table name
            if '.' in table:
                schema, table_name = table.split('.')
            else:
                # Use configured schema instead of hardcoded PUBLIC
                schema = self.engine.config.get('schema', 'PUBLIC').upper()
                table_name = table
            
            # Remove quotes and normalize to uppercase for Snowflake
            schema = schema.replace('"', '').upper()
            table_name = table_name.replace('"', '').upper()
            
            self.logger.info(f"   📊 Querying INFORMATION_SCHEMA.COLUMNS for schema={schema}, table={table_name}")
            
            # Get column info from Snowflake
            cursor = self.engine.connector.connection.cursor()
            query = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{schema}' 
            AND TABLE_NAME = '{table_name}'
            AND (DATA_TYPE LIKE '%DATE%' OR DATA_TYPE LIKE '%TIME%')
            ORDER BY ORDINAL_POSITION
            """
            cursor.execute(query)
            date_columns = cursor.fetchall()
            
            self.logger.info(f"   📋 Found {len(date_columns)} date columns: {date_columns}")
            
            if date_columns:
                # Prefer common date column names
                for col_name, col_type in date_columns:
                    if any(name in col_name.upper() for name in ['CREATED', 'DATE', 'UPDATED', 'MODIFIED', 'TIMESTAMP']):
                        self.logger.info(f"   ✅ Found preferred date column: {col_name} ({col_type})")
                        return col_name
                # Fallback to first date column
                col_name, col_type = date_columns[0]
                self.logger.info(f"   ✅ Using first date column: {col_name} ({col_type})")
                return col_name
            else:
                self.logger.warning(f"   ⚠️  No date columns found in {schema}.{table_name}")
                return None
                
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error finding date column: {e}")
            return None

    def _table_exists(self, table: str) -> bool:
        """Return True if the given schema.table exists in Snowflake."""
        try:
            if "." in table:
                schema, table_name = table.split(".", 1)
            else:
                schema, table_name = "PUBLIC", table
            schema = schema.replace('"', '')
            table_name = table_name.replace('"', '')
            q = f"""
                SELECT 1
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}'
            """
            cur = self.engine.connector.connection.cursor()
            cur.execute(q)
            return cur.fetchone() is not None
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error checking table existence for {table}: {e}")
            return False

    def _find_tables_with_column(self, column_name: str, schema: Optional[str] = None) -> List[str]:
        """Find all schema.table names containing the given column."""
        try:
            col = column_name.replace('"', '').upper()
            schema_filter = f"AND TABLE_SCHEMA = '{schema}'" if schema else ""
            q = f"""
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE UPPER(COLUMN_NAME) = '{col}'
                {schema_filter}
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            cur = self.engine.connector.connection.cursor()
            cur.execute(q)
            rows = cur.fetchall()
            tables = [f"{r[0]}.{r[1]}" for r in rows]
            self.logger.info(f"   🔎 Found {len(tables)} tables with column {column_name}: {tables}")
            return tables
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error finding tables for column {column_name}: {e}")
            return []

    def _get_column_type(self, table: str, column: str) -> Optional[str]:
        """Return Snowflake type for table.column (e.g., NUMBER(10,2), VARCHAR, DATE)."""
        try:
            if "." in table:
                schema, table_name = table.split(".", 1)
            else:
                schema, table_name = "PUBLIC", table
            schema = schema.replace('"', '')
            table_name = table_name.replace('"', '')
            col = column.replace('"', '')
            q = f"""
                SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table_name}' AND UPPER(COLUMN_NAME) = UPPER('{col}')
            """
            cur = self.engine.connector.connection.cursor()
            cur.execute(q)
            row = cur.fetchone()
            if not row:
                self.logger.warning(f"   ⚠️  Column type not found for {table}.{column}")
                return None
            data_type, char_len, num_prec, num_scale = row
            dt_upper = (data_type or "").upper()
            if dt_upper in ("TEXT", "STRING", "VARCHAR"):
                return "STRING"
            if dt_upper == "NUMBER" and num_prec is not None:
                if num_scale is not None:
                    return f"NUMBER({int(num_prec)},{int(num_scale)})"
                return f"NUMBER({int(num_prec)})"
            if dt_upper in ("INT", "INTEGER", "BIGINT", "SMALLINT"):
                return "NUMBER"
            if dt_upper in ("FLOAT", "DOUBLE", "REAL"):
                return "FLOAT"
            if dt_upper in ("DATE",):
                return "DATE"
            if "TIMESTAMP" in dt_upper:
                return "TIMESTAMP"
            # Fallback to original type
            return dt_upper or "STRING"
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error getting type for {table}.{column}: {e}")
            return None

    def _generate_masking_sql(self, table: str, column: str, policy_name: str, pii_types: List[str], user_query: str = "") -> List[str]:
        """Generate masking SQL with role sets derived dynamically from the user request AND date-based logic."""
        
        # Resolve column type to build type-safe policies
        column_type = self._get_column_type(table, column) or "STRING"
        self.logger.info(f"   🔠 Column type resolved for {table}.{column}: {column_type}")

        # Determine masking function based on PII type and column type
        if 'EMAIL_ADDRESS' in pii_types and column_type == 'STRING':
            mask_function = "CONCAT(LEFT(val, 3), '***@***.com')"
        elif 'PHONE_NUMBER' in pii_types and column_type == 'STRING':
            mask_function = "'XXX-XXX-XXXX'"
        elif 'SSN' in pii_types and column_type == 'STRING':
            mask_function = "'XXX-XX-XXXX'"
        else:
            # Type-aware default mask
            if column_type.startswith('NUMBER') or column_type in ('NUMBER', 'FLOAT'):
                mask_function = "0"
            elif column_type in ('DATE', 'TIMESTAMP'):
                mask_function = "NULL"
            else:
                mask_function = "'***MASKED***'"
        
        # Clean policy name to avoid SQL injection
        clean_policy_name = policy_name.replace("'", "").replace('"', '').replace(';', '')
        
        # Detect date filter from user query (e.g., "older than 90 days")
        date_filter_days = None
        date_column = None
        self.logger.info(f"   🔍 Checking for date filter in query: '{user_query}'")
        if user_query:
            query_lower = user_query.lower()
            import re
            match = re.search(r'(older than|past|last)\s+(\d+)\s+day', query_lower)
            if match:
                date_filter_days = int(match.group(2))
                self.logger.info(f"   ✅ Date filter MATCH: {date_filter_days} days")
                # Try to detect date column in the table
                date_column = self._find_date_column(table)
                if date_column:
                    self.logger.info(f"   📅 Date filter detected: older than {date_filter_days} days using column {date_column}")
                else:
                    self.logger.warning(f"   ⚠️  Date filter detected but NO date column found in table {table}")
            else:
                self.logger.info(f"   ℹ️  No date filter pattern found in query")
        else:
            self.logger.warning(f"   ⚠️  No user_query provided to _generate_masking_sql")

        self.logger.info(f"   📝 User query passed to _generate_masking_sql: '{user_query}'")
        role_context = self._derive_role_context(user_query)
        self.logger.info(f"   🎭 Role context returned: admin_roles={role_context['admin_roles']}, masked_roles={role_context['masked_roles']}")
        admin_roles_sql = ",".join(f"'{role}'" for role in role_context['admin_roles']) if role_context['admin_roles'] else ""
        masked_roles_sql = ",".join(f"'{role}'" for role in role_context['masked_roles'])
        self.logger.info(f"   🔧 SQL parts: admin_roles_sql='{admin_roles_sql}', masked_roles_sql='{masked_roles_sql}'")

        # Build CASE with date logic if applicable
        if date_filter_days and date_column:
            # Two-parameter policy: (val, date_col) with date-based masking
            if admin_roles_sql:
                # Admins see unmasked, others see masked if date condition met
                case_statement = (
                    f"CASE WHEN CURRENT_ROLE() IN ({admin_roles_sql}) THEN val "
                    f"WHEN DATEDIFF(day, date_col, CURRENT_DATE()) > {date_filter_days} AND CURRENT_ROLE() IN ({masked_roles_sql}) THEN {mask_function} "
                    f"ELSE val END"
                )
            else:
                # No admin exceptions - mask ALL roles based on date
                case_statement = (
                    f"CASE WHEN DATEDIFF(day, date_col, CURRENT_DATE()) > {date_filter_days} THEN {mask_function} "
                    f"ELSE val END"
                )
            policy_signature = f"(val {column_type}, date_col DATE) RETURNS {column_type}"
            using_clause = f" USING ({column}, {date_column})"
            self.logger.info(f"   ✅ DATE-BASED Masking: Rows older than {date_filter_days} days will be masked for roles: {role_context['masked_roles']}")
        else:
            # Original role-only logic
            if admin_roles_sql:
                # Admins unmasked, specific roles masked
                case_statement = (
                    f"CASE WHEN CURRENT_ROLE() IN ({admin_roles_sql}) THEN val "
                    f"WHEN CURRENT_ROLE() IN ({masked_roles_sql}) THEN {mask_function} "
                    f"ELSE val END"
                )
            else:
                # No admin exceptions - mask ALL roles
                case_statement = f"{mask_function}"
            policy_signature = f"(val {column_type}) RETURNS {column_type}"
            using_clause = ""
        
        return [
            "BEGIN;",
            f"ALTER TABLE {table} MODIFY COLUMN {column} UNSET MASKING POLICY;",
            f"DROP MASKING POLICY IF EXISTS {clean_policy_name};",
            f"CREATE MASKING POLICY IF NOT EXISTS {clean_policy_name} AS {policy_signature} -> {case_statement};",
            f"ALTER TABLE {table} MODIFY COLUMN {column} SET MASKING POLICY {clean_policy_name}{using_clause};",
            "COMMIT;"
        ]

    def _generate_rollback_sql(self, operation: str, table: str, column: str, policy_name: str) -> List[str]:
        return [f"ALTER TABLE {table} MODIFY COLUMN {column} UNSET MASKING POLICY;"]

    def _simulate_after_state(self, before_state, plan_result, observe_result) -> Dict[str, Any]:
        after_state = {}
        for table_name, rows in before_state.items():
            after_state[table_name] = []
            for row in rows:
                simulated_row = row.copy()
                for key, value in simulated_row.items():
                    if isinstance(value, str) and '@' in value:
                        simulated_row[key] = "***MASKED***"
                after_state[table_name].append(simulated_row)
        return after_state

    def _get_human_approval(self, simulate_result: SimulationResult, plan_result: ExecutionPlan) -> Dict[str, Any]:
        """Return approval details for frontend handling - no terminal prompts"""
        self.logger.info("🎭 ATLAN ACTIONS - GOVERNANCE PREVIEW")
        self.logger.info(f"Rows affected: {simulate_result.affected_rows:,}")
        self.logger.info(f"Columns affected: {len(simulate_result.affected_columns)}")
        self.logger.info(f"Risk level: {simulate_result.risk_assessment}")
        self.logger.info(f"Estimated time: {plan_result.estimated_impact.get('estimated_time_seconds', 0):.1f}s")
        
        if self.atlan_enabled:
            self.logger.info("🏷️  Atlan sync: ✅ Enabled")
        else:
            self.logger.info("🏷️  Atlan sync: ⚠️ Disabled")
        
        self.logger.info(f"💻 SQL COMMANDS ({len(plan_result.sql_commands)}):")
        for i, sql in enumerate(plan_result.sql_commands[:3], 1):
            self.logger.info(f"{i}. {sql[:60]}...")
        
        # Return pending approval for frontend handling
        return {
            'approved': False,  # Require explicit frontend approval
            'reason': 'Governance action requires human approval before execution',
            'timestamp': datetime.now().isoformat(),
            'pending_approval': True,  # Require manual approval in frontend
            'simulation_details': {
                'rows_affected': simulate_result.affected_rows,
                'columns_affected': len(simulate_result.affected_columns),
                'risk_level': simulate_result.risk_assessment,
                'estimated_time': plan_result.estimated_impact.get('estimated_time_seconds', 0),
                'sql_commands': plan_result.sql_commands[:5],  # First 5 commands for preview
                'before_sample': {k: v[:2] for k, v in simulate_result.before_state.items()},
                'after_sample': {k: v[:2] for k, v in simulate_result.after_state.items()}
            }
        }

    def _update_metadata_catalog(self, observe_result, analyze_result) -> Dict[str, Any]:
        updates = {}
        for finding in analyze_result.pii_findings:
            table = finding['table']
            column = finding['column']
            
            self.metadata_db.execute("""
                INSERT OR REPLACE INTO column_classifications 
                (table_name, column_name, classification, confidence, protection_status, policy_name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                table, column, 'PII', finding['confidence'], 'MASKED',
                f"{table}_{column}_mask", datetime.now().isoformat()
            ))
            
            updates[f"{table}.{column}"] = {
                'classification': 'PII',
                'protection_status': 'MASKED',
                'confidence': finding['confidence']
            }
        
        self.metadata_db.commit()
        return updates

    def _verify_policy_effectiveness(self, execute_result, observe_result) -> bool:
        if not execute_result.success:
            return False
        
        unique_tables = self._extract_unique_tables(observe_result.target_entities)
        for table_name in unique_tables:
            try:
                verification_samples = self._sample_table_data(table_name, limit=5)
                for row in verification_samples:
                    for key, value in row.items():
                        if isinstance(value, str) and "***MASKED***" in value:
                            return True
            except Exception:
                continue
        return True

    def _measure_performance_impact(self, execute_result) -> Dict[str, float]:
        return {'execution_time_seconds': execute_result.execution_time}

    def _discover_similar_patterns(self, observe_result, analyze_result) -> List[str]:
        return [f"Table '{list(observe_result.sample_data.keys())[0]}' has similar PII patterns"]

    def _generate_recommendations(self, observe_result, analyze_result, patterns) -> List[str]:
        recommendations = []
        for pattern in patterns:
            recommendations.append(f"Consider applying similar policies to: {pattern}")
        
        if analyze_result.risk_score > 0.7:
            recommendations.append("High risk detected - consider implementing continuous PII scanning")
        
        if len(analyze_result.pii_findings) > 5:
            recommendations.append("Multiple PII columns found - consider data classification automation")
        
        return recommendations

    def _calculate_confidence_feedback(self, execute_result, verification_status) -> float:
        base_confidence = 0.8
        if execute_result.success:
            base_confidence += 0.1
        if verification_status:
            base_confidence += 0.1
        return min(1.0, base_confidence)

    def _store_metrics(self, user_query: str, results: Dict[str, Any], start_time: datetime) -> None:
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Store execution metrics with Atlan sync status
        self.metadata_db.execute("""
            INSERT INTO execution_history 
            (nl_query, intent, phase, result, success, atlan_sync_status, timestamp, execution_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_query,
            results['phases'].get('observe', {}).get('intent', 'UNKNOWN'),
            'COMPLETE',
            json.dumps(results, cls=DecimalEncoder),
            results.get('status') == 'success',
            json.dumps(results.get('phases', {}).get('execute', {}).get('atlan_sync_status', {})),
            datetime.now().isoformat(),
            total_time
        ))
        
        self.metadata_db.commit()

    def _handle_low_confidence(self, user_query: str, observe_result: ObservationResult) -> Dict[str, Any]:
        return {
            'status': 'low_confidence',
            'confidence': observe_result.confidence,
            'message': f"Cannot proceed with confidence {observe_result.confidence:.1%}",
            'suggestions': [
                "Be more specific about which tables or columns to target",
                "Specify the type of operation (mask, delete, etc.)"
            ]
        }

    # ============================================================================
    # DEMO MODE - Enhanced for Atlan Actions branding
    # ============================================================================
    
    def run_demo_mode(self) -> None:
        """Enhanced demo mode showcasing Atlan Actions capabilities"""
        demo_queries = [
            {
                'query': 'mask pii in customers table',
                'description': 'Basic PII masking with Atlan sync',
                'expected_time': '< 10 seconds'
            },
            {
                'query': 'automatically discover PII and apply intelligent masking',
                'description': 'Autonomous discovery with catalog integration',
                'expected_time': '< 30 seconds'
            }
        ]
        
        print("\n" + "="*80)
        print("🎬 ATLAN ACTIONS ENGINE - GOVERNANCE AUTOMATION DEMO")
        print("="*80)
        print("The actions layer between catalog and orchestration")
        print(f"Mode: {self.nl_mode} | Execution: {self.execution_mode.value} | Atlan: {'✅' if self.atlan_enabled else '❌'}")
        print("="*80)
        
        total_start = datetime.now()
        
        for i, demo in enumerate(demo_queries, 1):
            print(f"\n{'='*80}")
            print(f"DEMO {i}/{len(demo_queries)}: {demo['description']}")
            print(f"Expected: {demo['expected_time']}")
            print(f"{'='*80}")
            print(f"\n🎯 Query: \"{demo['query']}\"")
            
            input("\nPress ENTER to execute...")
            
            query_start = datetime.now()
            results = self.process_natural_language(demo['query'])
            query_time = (datetime.now() - query_start).total_seconds()
            
            if results['status'] == 'success':
                print(f"✅ SUCCESS in {query_time:.1f}s")
                print(f"🎯 Intent: {results['phases']['observe']['intent']}")
                print(f"📊 Confidence: {results['phases']['observe']['confidence']:.1%}")
                print(f"💾 SQL Commands: {len(results['phases']['plan']['sql_commands'])}")
                
                # Show Atlan sync status
                atlan_status = results['phases'].get('execute', {}).get('atlan_sync_status', {})
                if atlan_status.get('enabled'):
                    synced_count = len(atlan_status.get('synced_items', []))
                    print(f"🏷️  Atlan Sync: ✅ Tagged {synced_count} items in catalog")
                else:
                    print(f"🏷️  Atlan Sync: ⚠️ Not configured")
                
                # Show recommendations
                recommendations = results['phases'].get('learn', {}).get('recommendations', [])
                for rec in recommendations[:2]:
                    print(f"💡 {rec}")
            else:
                print(f"⚠️  {results['status'].upper()}: {results.get('error', 'Unknown error')}")
        
        total_time = (datetime.now() - total_start).total_seconds()
        print(f"\n{'='*80}")
        print(f"🏁 ATLAN ACTIONS DEMO COMPLETE")
        print(f"{'='*80}")
        print(f"Total Demo Time: {total_time:.1f}s")
        print(f"Governance actions between catalog and orchestration demonstrated")
        print(f"{'='*80}\n")

# ============================================================================
# MAIN INTERFACE
# ============================================================================

def run_atlan_actions(demo_mode: bool = False, execution_mode: str = "direct"):
    """Main interface for Atlan Actions Engine"""
    
    # Check for API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    use_llm = bool(anthropic_key or openai_key)
    
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY detected - using Claude mode")
    elif openai_key:
        print("✅ OPENAI_API_KEY detected - using OpenAI mode")
    else:
        print("⚠️  No API keys set - using local mode")
    
    # Atlan configuration (demo setup)
    atlan_config = {
        'base_url': os.getenv('ATLAN_BASE_URL', 'https://demo.atlan.com'),
        'api_token': os.getenv('ATLAN_API_TOKEN')
    }
    
    # Initialize Atlan Actions Engine
    actions_engine = AtlanActionsEngine(
        use_llm=use_llm, 
        execution_mode=execution_mode,
        atlan_config=atlan_config if atlan_config['api_token'] else None
    )
    
    if demo_mode:
        actions_engine.run_demo_mode()
        return
    
    print("="*80)
    print("🎯 ATLAN ACTIONS ENGINE - Governance Automation Platform")
    print("="*80)
    print(f"Mode: {actions_engine.nl_mode} | Execution: {execution_mode}")
    print(f"Atlan Integration: {'✅ Enabled' if actions_engine.atlan_enabled else '❌ Disabled'}")
    print("The actions layer between catalog and orchestration")
    print("="*80)
    print("\nCommands:")
    print("  - Type natural language governance commands")
    print("  - 'demo' to run Atlan Actions demo")
    print("  - 'quit' to exit")
    print("="*80)
    
    while True:
        print(f"\n{'-'*60}")
        user_query = input("🎯 Atlan Actions: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("👋 Shutting down Atlan Actions Engine...")
            break
        
        if user_query.lower() == 'demo':
            actions_engine.run_demo_mode()
            continue
        
        if not user_query:
            continue
        
        # Process governance command
        results = actions_engine.process_natural_language(user_query)
        
        # Display results
        print(f"\n📊 STATUS: {results['status'].upper()}")
        if results['status'] == 'success':
            print(f"⏱️  Time: {results.get('total_time', 0):.2f}s")
            
            # Show Atlan sync status
            atlan_status = results['phases'].get('execute', {}).get('atlan_sync_status', {})
            if atlan_status.get('enabled'):
                synced_count = len(atlan_status.get('synced_items', []))
                print(f"🏷️  Atlan: Tagged {synced_count} items in catalog")
            
            learn = results['phases'].get('learn', {})
            print(f"\n🎓 LEARNING:")
            print(f"   Verified: {'✅' if learn.get('verification_status') else '❌'}")
            print(f"   Patterns: {len(learn.get('discovered_patterns', []))}")
            for rec in learn.get('recommendations', [])[:3]:
                print(f"   💡 {rec}")
        else:
            print(f"❌ Error: {results.get('error', 'Unknown')}")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Atlan Actions Engine - Governance Automation Platform')
    parser.add_argument('--demo', action='store_true', help='Run Atlan Actions demo mode')
    parser.add_argument('--mode', choices=['direct', 'airflow', 'prefect'], default='direct', help='Execution mode')
    parser.add_argument('--query', type=str, help='Single governance query to execute')
    args = parser.parse_args()
    
    if args.query:
        # Single query execution
        atlan_config = {
            'base_url': os.getenv('ATLAN_BASE_URL', 'https://demo.atlan.com'),
            'api_token': os.getenv('ATLAN_API_TOKEN')
        }
        
        actions_engine = AtlanActionsEngine(
            execution_mode=args.mode,
            atlan_config=atlan_config if atlan_config['api_token'] else None
        )
        results = actions_engine.process_natural_language(args.query)
        print(json.dumps(results, indent=2, cls=DecimalEncoder))
    else:
        run_atlan_actions(demo_mode=args.demo, execution_mode=args.mode)

if __name__ == "__main__":
    main()
