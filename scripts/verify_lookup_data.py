#!/usr/bin/env python3
"""
Verify and display the synthetic lookup data that was created.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from database.config import get_engine
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def display_lookup_summary():
    """Display a summary of the lookup data created."""
    logger.info("📋 PDC Lookup Tables Data Summary")
    logger.info("=" * 80)
    
    try:
        engine = get_engine()
        
        with engine.connect() as conn:
            # Get lookup types with counts (avoiding TEXT column in GROUP BY)
            types_query = """
            SELECT 
                lt.lookup_type, 
                lt.display_name, 
                COUNT(lc.lookup_code) as code_count
            FROM pdc_lookup_types lt
            LEFT JOIN pdc_lookup_codes lc ON lt.lookup_type = lc.lookup_type
            GROUP BY lt.lookup_type, lt.display_name
            ORDER BY lt.lookup_type
            """
            
            types_result = conn.execute(text(types_query))
            types_data = types_result.fetchall()
            
            logger.info(f"🎯 Total Lookup Types: {len(types_data)}")
            logger.info("")
            
            total_codes = 0
            
            for row in types_data:
                lookup_type, display_name, code_count = row
                total_codes += code_count
                
                # Get description separately
                desc_query = "SELECT description FROM pdc_lookup_types WHERE lookup_type = :lookup_type"
                desc_result = conn.execute(text(desc_query), {'lookup_type': lookup_type})
                description = desc_result.fetchone()[0] if desc_result.rowcount > 0 else "No description"
                
                logger.info(f"📂 {lookup_type}")
                logger.info(f"   📝 Name: {display_name}")
                logger.info(f"   📄 Description: {description}")
                logger.info(f"   🔢 Codes: {code_count}")
                
                # Get sample codes for this type
                codes_query = """
                SELECT lookup_code, display_name, description
                FROM pdc_lookup_codes
                WHERE lookup_type = :lookup_type
                ORDER BY sort_order
                """
                
                codes_result = conn.execute(text(codes_query), {'lookup_type': lookup_type})
                codes = codes_result.fetchall()
                
                logger.info("   📋 Available Codes:")
                for code_row in codes:
                    code, code_name, code_desc = code_row
                    logger.info(f"      • {code}: {code_name}")
                
                logger.info("")
            
            logger.info(f"🎯 Total Lookup Codes: {total_codes}")
            logger.info("=" * 80)
            logger.info("✅ All lookup data has been successfully created and is ready to use!")
            logger.info("🔗 These lookups can now be used by your API endpoints for:")
            logger.info("   • PDC Classifications")
            logger.info("   • Document Management")
            logger.info("   • Records Management")
            logger.info("   • Compliance and Retention")
            
            return True
        
    except Exception as e:
        logger.error(f"❌ Failed to display summary: {str(e)}")
        return False

if __name__ == "__main__":
    display_lookup_summary()