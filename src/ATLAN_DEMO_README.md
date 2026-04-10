# Atlan Actions Engine - Demo Guide

🎯 **The governance automation layer between Atlan catalog and orchestration systems**

## 🚀 Quick Start

### Option 1: Interactive Demo Runner
```bash
python run_atlan_demo.py
```

### Option 2: Direct Demo Execution
```bash
# Quick 5-minute demo
python atlan_actions_demo.py --quick

# Full executive demo (15 minutes)
python atlan_actions_demo.py --full

# Interactive natural language mode
python atlan_ai_control_plane.py --demo
```

## 🔧 Setup (Optional but Recommended)

### AI API Configuration
```bash
# For enhanced natural language processing
export ANTHROPIC_API_KEY="your_claude_key"
# OR
export OPENAI_API_KEY="your_openai_key"
```

### Atlan Integration
```bash
# For real catalog synchronization
export ATLAN_BASE_URL="https://your-tenant.atlan.com"
export ATLAN_API_TOKEN="your_atlan_token"
```

### Database Connection
Configure `config.yaml` with your Snowflake/BigQuery credentials (optional - demo works with mock data)

## 🎭 Demo Scenarios

### 1. Quick Demo (5 minutes)
- Basic PII masking demonstration
- Atlan catalog sync showcase
- Natural language command processing

### 2. Executive Demo (15 minutes)
- **Scenario 1**: Basic PII masking with catalog sync
- **Scenario 2**: Autonomous discovery & classification
- **Scenario 3**: Multi-mode execution (Direct vs Airflow)
- **Scenario 4**: Learning engine & recommendations
- Business value summary and ROI discussion

### 3. Interactive Mode
Direct command interface for testing:
```
🎯 Atlan Actions: mask pii in customers table
🎯 Atlan Actions: automatically discover and protect sensitive data
🎯 Atlan Actions: generate airflow dag for email masking
```

## 🏗️ Architecture Overview

```
Data Sources → Atlan Catalog → ATLAN ACTIONS → Orchestration (Airflow/Prefect)
                                   ↓
                            6-Phase Governance Loop:
                            OBSERVE → ANALYZE → PLAN 
                            → SIMULATE → EXECUTE → LEARN
```

## 🎯 Key Features Demonstrated

### ✅ Natural Language Processing
- Convert governance commands to executable SQL
- Intent recognition and entity extraction
- Confidence scoring and validation

### ✅ Atlan Catalog Integration
- Real-time PII classification tagging
- Governance lineage creation
- Custom metadata synchronization

### ✅ Multi-Mode Execution
- **Direct**: Immediate policy deployment
- **Airflow**: DAG generation for orchestration
- **Prefect**: Flow generation (coming soon)

### ✅ 6-Phase Autonomous Governance
1. **OBSERVE**: Schema analysis and data sampling
2. **ANALYZE**: ML-powered PII detection
3. **PLAN**: SQL generation and execution planning
4. **SIMULATE**: Impact preview and risk assessment
5. **EXECUTE**: Policy deployment with Atlan sync
6. **LEARN**: Pattern discovery and recommendations

## 📊 Expected Demo Results

### Performance Metrics
- **Basic PII Masking**: 2-5 seconds
- **Autonomous Discovery**: 10-30 seconds
- **Atlan Sync**: 1-3 seconds per entity
- **Success Rate**: 95%+ with proper configuration

### Business Value
- **Speed**: Reduce policy creation from hours to seconds
- **Intelligence**: AI-powered discovery and classification
- **Integration**: Seamless catalog and orchestration connectivity
- **Learning**: Continuous improvement through ML patterns

## 🛠️ Execution Modes

### Direct Mode
```python
actions_engine = AtlanActionsEngine(execution_mode="direct")
results = actions_engine.process_natural_language("mask pii in customers")
```

### Airflow Mode
```python
actions_engine = AtlanActionsEngine(execution_mode="airflow")
results = actions_engine.process_natural_language("mask pii in customers")
# Generates Airflow DAG code instead of executing directly
```

## 📈 Demo Customization

### Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude AI processing | Local fallback |
| `OPENAI_API_KEY` | OpenAI processing | Local fallback |
| `ATLAN_BASE_URL` | Atlan tenant URL | https://demo.atlan.com |
| `ATLAN_API_TOKEN` | Atlan API access | Demo mode only |

### Configuration Files
- `config.yaml`: Database connections
- `atlan_actions_metadata.db`: Local learning storage

## 🎬 Demo Tips

### For Technical Audiences
- Show the 6-phase governance loop in detail
- Demonstrate SQL generation and execution
- Highlight Atlan API integration code
- Show Airflow DAG generation

### For Business Audiences
- Focus on natural language commands
- Emphasize speed and automation
- Show before/after governance states
- Highlight ROI and efficiency gains

### For Executive Presentations
- Use the full 15-minute executive demo
- Focus on business value and positioning
- Show integration between catalog and orchestration
- Emphasize "actions layer" positioning

## 🔍 Troubleshooting

### Common Issues
1. **No AI API keys**: Demo runs with local fallback (reduced accuracy)
2. **No Atlan token**: Demo mode only (no real catalog sync)
3. **No database**: Uses mock data (limited functionality)
4. **Import errors**: Ensure all dependencies installed

### Debug Mode
```bash
# Add verbose logging
export ATLAN_DEBUG=true
python atlan_actions_demo.py --full
```

## 📞 Support

For demo support or questions:
- Check the interactive help: `python run_atlan_demo.py`
- Review the documentation option in the demo menu
- Test individual features using the feature testing option

---

🎯 **Atlan Actions Engine**: Bridging the gap between catalog discovery and governance execution through intelligent automation.