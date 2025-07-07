#!/usr/bin/env python3
"""
Admin Interface for Messages from Beyond System
Allows manual input of external messages for agent interpretation
"""

import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class MessageBeyondAdmin:
    """Admin interface for managing messages from beyond"""
    
    def __init__(self, db_path: str = "data/religion_memory.db"):
        self.db_path = Path(db_path)
        self.ensure_tables_exist()
    
    def ensure_tables_exist(self):
        """Create tables if they don't exist"""
        schema_path = Path("messages_beyond_schema.sql")
        if not schema_path.exists():
            print("Warning: Schema file not found. Creating basic schema.")
            self._create_basic_schema()
            return
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Execute schema (split by semicolon and filter empty statements)
        statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
        for statement in statements:
            try:
                cursor.execute(statement)
            except sqlite3.Error as e:
                if "already exists" not in str(e):
                    print(f"Schema error: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Database schema verified/created")
    
    def _create_basic_schema(self):
        """Create basic schema if file doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages_from_beyond (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                content TEXT NOT NULL,
                source_label TEXT DEFAULT 'Beyond',
                cycle_number INTEGER,
                admin_notes TEXT,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_reflections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                reflection_text TEXT NOT NULL,
                sentiment_score REAL,
                theological_impact TEXT,
                confidence_change REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_message(self, content: str, source_label: str = "Beyond", 
                   admin_notes: str = None, cycle_number: int = None) -> str:
        """Add a new message from beyond"""
        message_id = str(uuid.uuid4())[:12]  # Shorter ID for readability
        timestamp = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages_from_beyond 
            (message_id, timestamp, content, source_label, cycle_number, admin_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, timestamp, content, source_label, cycle_number, admin_notes))
        
        # Initialize processing record
        cursor.execute("""
            INSERT INTO message_processing (message_id, processing_started_at)
            VALUES (?, ?)
        """, (message_id, timestamp))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Message added with ID: {message_id}")
        print(f"📝 Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        print(f"🏷️  Source: {source_label}")
        
        return message_id
    
    def list_messages(self, limit: int = 10, show_processed: bool = True) -> List[Dict]:
        """List recent messages"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        where_clause = "" if show_processed else "WHERE processed = FALSE"
        
        cursor.execute(f"""
            SELECT * FROM messages_from_beyond 
            {where_clause}
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def get_message_details(self, message_id: str) -> Dict:
        """Get detailed information about a message including agent responses"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get message
        cursor.execute("SELECT * FROM messages_from_beyond WHERE message_id = ?", (message_id,))
        message = dict(cursor.fetchone() or {})
        
        if not message:
            return {}
        
        # Get reflections
        cursor.execute("""
            SELECT * FROM message_reflections 
            WHERE message_id = ? 
            ORDER BY created_at
        """, (message_id,))
        message['reflections'] = [dict(row) for row in cursor.fetchall()]
        
        # Get discussions
        cursor.execute("""
            SELECT * FROM message_discussions 
            WHERE message_id = ? 
            ORDER BY discussion_round, timestamp
        """, (message_id,))
        message['discussions'] = [dict(row) for row in cursor.fetchall()]
        
        # Get influences
        cursor.execute("""
            SELECT * FROM message_influences 
            WHERE message_id = ? 
            ORDER BY created_at
        """, (message_id,))
        message['influences'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return message
    
    def mark_processed(self, message_id: str):
        """Mark a message as processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages_from_beyond 
            SET processed = TRUE 
            WHERE message_id = ?
        """, (message_id,))
        
        cursor.execute("""
            UPDATE message_processing 
            SET processing_completed_at = ? 
            WHERE message_id = ?
        """, (datetime.now(), message_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Message {message_id} marked as processed")
    
    def delete_message(self, message_id: str):
        """Delete a message and all related data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete in order due to foreign keys
        cursor.execute("DELETE FROM message_influences WHERE message_id = ?", (message_id,))
        cursor.execute("DELETE FROM message_discussions WHERE message_id = ?", (message_id,))
        cursor.execute("DELETE FROM message_reflections WHERE message_id = ?", (message_id,))
        cursor.execute("DELETE FROM message_processing WHERE message_id = ?", (message_id,))
        cursor.execute("DELETE FROM messages_from_beyond WHERE message_id = ?", (message_id,))
        
        conn.commit()
        conn.close()
        
        print(f"🗑️  Message {message_id} deleted")
    
    def interactive_add(self):
        """Interactive message addition"""
        print("\n=== Add Message from Beyond ===")
        
        content = input("📝 Enter message content: ").strip()
        if not content:
            print("❌ Content cannot be empty")
            return
        
        source_label = input("🏷️  Source label (default: Beyond): ").strip() or "Beyond"
        admin_notes = input("📋 Admin notes (optional): ").strip() or None
        
        cycle_input = input("🔄 Current cycle number (optional): ").strip()
        cycle_number = int(cycle_input) if cycle_input.isdigit() else None
        
        message_id = self.add_message(content, source_label, admin_notes, cycle_number)
        
        print(f"\n🎯 Trigger agent reflection? (y/N): ", end="")
        if input().lower().startswith('y'):
            print("📨 Message ready for agent processing")
            print("💡 Run the orchestrator to trigger reflection session")
    
    def show_status(self):
        """Show system status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM messages_from_beyond")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages_from_beyond WHERE processed = TRUE")
        processed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM message_reflections")
        reflections = cursor.fetchone()[0]
        
        conn.close()
        
        print("\n=== Messages from Beyond - Status ===")
        print(f"📊 Total messages: {total}")
        print(f"✅ Processed: {processed}")
        print(f"⏳ Pending: {total - processed}")
        print(f"💭 Total reflections: {reflections}")


def main():
    parser = argparse.ArgumentParser(description="Admin interface for Messages from Beyond")
    parser.add_argument("--db", default="data/religion_memory.db", help="Database path")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add message
    add_parser = subparsers.add_parser("add", help="Add a new message")
    add_parser.add_argument("content", help="Message content")
    add_parser.add_argument("--source", default="Beyond", help="Source label")
    add_parser.add_argument("--notes", help="Admin notes")
    add_parser.add_argument("--cycle", type=int, help="Cycle number")
    
    # List messages
    list_parser = subparsers.add_parser("list", help="List messages")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of messages")
    list_parser.add_argument("--all", action="store_true", help="Include processed messages")
    
    # Show details
    detail_parser = subparsers.add_parser("show", help="Show message details")
    detail_parser.add_argument("message_id", help="Message ID")
    
    # Mark processed
    process_parser = subparsers.add_parser("process", help="Mark message as processed")
    process_parser.add_argument("message_id", help="Message ID")
    
    # Delete message
    delete_parser = subparsers.add_parser("delete", help="Delete message")
    delete_parser.add_argument("message_id", help="Message ID")
    
    # Interactive mode
    subparsers.add_parser("interactive", help="Interactive message input")
    
    # Status
    subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    admin = MessageBeyondAdmin(args.db)
    
    if args.command == "add":
        admin.add_message(args.content, args.source or "Beyond", args.notes, args.cycle)
    
    elif args.command == "list":
        messages = admin.list_messages(args.limit, args.all)
        print(f"\n=== Messages from Beyond ({len(messages)} shown) ===")
        for msg in messages:
            status = "✅" if msg['processed'] else "⏳"
            print(f"{status} {msg['message_id']} - {msg['timestamp'][:16]} - {msg['source_label']}")
            print(f"   {msg['content'][:80]}{'...' if len(msg['content']) > 80 else ''}")
    
    elif args.command == "show":
        details = admin.get_message_details(args.message_id)
        if details:
            print(f"\n=== Message Details: {details['message_id']} ===")
            print(f"📅 Time: {details['timestamp']}")
            print(f"🏷️  Source: {details['source_label']}")
            print(f"📝 Content: {details['content']}")
            print(f"📋 Notes: {details.get('admin_notes', 'None')}")
            print(f"✅ Processed: {details['processed']}")
            
            if details['reflections']:
                print(f"\n💭 Agent Reflections ({len(details['reflections'])}):")
                for ref in details['reflections']:
                    print(f"  {ref['agent_id']}: {ref['reflection_text'][:100]}...")
        else:
            print(f"❌ Message {args.message_id} not found")
    
    elif args.command == "process":
        admin.mark_processed(args.message_id)
    
    elif args.command == "delete":
        admin.delete_message(args.message_id)
    
    elif args.command == "interactive":
        admin.interactive_add()
    
    elif args.command == "status":
        admin.show_status()
    
    else:
        # Default to interactive mode
        admin.interactive_add()


if __name__ == "__main__":
    main()