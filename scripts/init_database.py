#!/usr/bin/env python3
"""
Database initialization script for Code Review Quest
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.init_db import init_database
import logging

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🗄️ Initializing Code Review Quest Database...")
    print("=" * 50)
    
    try:
        init_database()
        print("\n✅ Database initialization completed successfully!")
        print("\n🎮 Your Code Review Quest database is ready!")
        print("   - Problems loaded and ready")
        print("   - Badges system configured")
        print("   - Demo user created")
        print("   - All tables created")
        
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)
