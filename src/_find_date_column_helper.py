# Helper method to add to ai_control_plane.py

def _find_date_column(self, table: str) -> Optional[str]:
    """Find a date/timestamp column in the table for date-based filtering"""
    try:
        # Parse table name
        if '.' in table:
            schema, table_name = table.split('.')
        else:
            schema = 'PUBLIC'
            table_name = table
        
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
        
        if date_columns:
            # Prefer common date column names
            for col_name, col_type in date_columns:
                if any(name in col_name.upper() for name in ['CREATED', 'DATE', 'UPDATED', 'MODIFIED', 'TIMESTAMP']):
                    self.logger.info(f"   ✅ Found date column: {col_name} ({col_type})")
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
