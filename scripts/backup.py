#!/usr/bin/env python
"""
Database backup utility.
Run: python scripts/backup.py
"""
import os
import sys
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app('production')

def backup_database():
    """Create a backup of the SQLite database."""
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        if not db_uri.startswith('sqlite:///'):
            print("⚠️  Backup only supported for SQLite databases")
            print(f"   Current database: {db_uri}")
            return
        
        db_path = db_uri.replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found: {db_path}")
            return
        
        # Create backups directory
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database
        shutil.copy2(db_path, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        
        # List recent backups
        backups = sorted(os.listdir(backup_dir), reverse=True)
        print(f"\n📁 Recent backups:")
        for backup in backups[:5]:
            size = os.path.getsize(os.path.join(backup_dir, backup))
            print(f"   - {backup} ({size:,} bytes)")

if __name__ == '__main__':
    backup_database()
