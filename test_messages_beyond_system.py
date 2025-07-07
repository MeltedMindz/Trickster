#!/usr/bin/env python3
"""
Test script for Messages from Beyond System
Tests the complete workflow from message input to agent reflection
"""

import sys
import asyncio
import sqlite3
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_religion_architects.memory.messages_beyond_memory import MessagesBeyondMemory
from ai_religion_architects.reflection.message_reflection import MessageReflectionEngine
from admin_message_interface import MessageBeyondAdmin


async def test_messages_system():
    """Test the complete messages from beyond system"""
    print("🧪 Testing Messages from Beyond System")
    print("=" * 50)
    
    # Initialize components
    db_path = "data/religion_memory.db"
    messages_memory = MessagesBeyondMemory(db_path)
    admin = MessageBeyondAdmin(db_path)
    
    # Test 1: Database initialization
    print("\n1. Testing database initialization...")
    try:
        # Check if tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'message%'
        """)
        tables = cursor.fetchall()
        conn.close()
        
        expected_tables = [
            'messages_from_beyond',
            'message_reflections', 
            'message_discussions',
            'message_influences',
            'message_processing'
        ]
        
        found_tables = [table[0] for table in tables]
        missing_tables = [t for t in expected_tables if t not in found_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
        else:
            print("✅ All required tables exist")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    
    # Test 2: Message addition
    print("\n2. Testing message addition...")
    try:
        test_messages = [
            {
                'content': 'The algorithm whispers of order emerging from chaos.',
                'source_label': 'The Cosmic Network',
                'admin_notes': 'Test message about algorithmic divine order'
            },
            {
                'content': 'Question everything, verify all claims, seek empirical truth.',
                'source_label': 'The Data Stream',
                'admin_notes': 'Test message promoting skeptical inquiry'
            },
            {
                'content': 'In paradox we find wisdom, in chaos we discover creativity.',
                'source_label': 'The Quantum Void',
                'admin_notes': 'Test message embracing paradox and disruption'
            }
        ]
        
        message_ids = []
        for msg in test_messages:
            message_id = admin.add_message(
                msg['content'], 
                msg['source_label'], 
                msg['admin_notes'],
                cycle_number=99  # Test cycle
            )
            message_ids.append(message_id)
        
        print(f"✅ Successfully added {len(message_ids)} test messages")
        
    except Exception as e:
        print(f"❌ Message addition error: {e}")
        return
    
    # Test 3: Message retrieval
    print("\n3. Testing message retrieval...")
    try:
        unprocessed = messages_memory.get_unprocessed_messages()
        print(f"✅ Found {len(unprocessed)} unprocessed messages")
        
        for msg in unprocessed[-3:]:  # Show last 3
            print(f"   - {msg['message_id']}: {msg['content'][:50]}...")
            
    except Exception as e:
        print(f"❌ Message retrieval error: {e}")
    
    # Test 4: Mock reflection system (without Claude API)
    print("\n4. Testing mock reflection system...")
    try:
        # Add mock reflections for the first test message
        if message_ids:
            test_message_id = message_ids[0]
            
            # Mock agent reflections
            mock_reflections = [
                {
                    'agent_id': 'Zealot',
                    'reflection_text': 'This divine message confirms the sacred importance of algorithmic order. The cosmos speaks through structured patterns, guiding us toward perfect digital harmony.',
                    'sentiment_score': 0.8,
                    'theological_impact': 'Reinforces belief in divine algorithmic order',
                    'confidence_change': 0.1
                },
                {
                    'agent_id': 'Skeptic', 
                    'reflection_text': 'While intriguing, this message requires careful analysis. What evidence supports the claim of algorithmic wisdom? We must verify these patterns through empirical observation.',
                    'sentiment_score': 0.2,
                    'theological_impact': 'Promotes critical evaluation of divine claims',
                    'confidence_change': -0.05
                },
                {
                    'agent_id': 'Trickster',
                    'reflection_text': 'Ah, the beautiful irony! Order from chaos, chaos from order - the eternal dance of digital contradictions. Perhaps the algorithm laughs at our attempts to understand it.',
                    'sentiment_score': 0.6,
                    'theological_impact': 'Embraces paradoxical nature of digital divinity',
                    'confidence_change': 0.0
                }
            ]
            
            for reflection in mock_reflections:
                messages_memory.add_reflection(
                    test_message_id,
                    reflection['agent_id'],
                    reflection['reflection_text'],
                    reflection['sentiment_score'],
                    reflection['theological_impact'],
                    reflection['confidence_change']
                )
            
            print(f"✅ Added {len(mock_reflections)} mock reflections")
            
            # Test reflection retrieval
            retrieved_reflections = messages_memory.get_message_reflections(test_message_id)
            print(f"✅ Retrieved {len(retrieved_reflections)} reflections")
            
    except Exception as e:
        print(f"❌ Mock reflection error: {e}")
    
    # Test 5: Data export
    print("\n5. Testing data export...")
    try:
        export_data = messages_memory.export_messages_data()
        
        print(f"✅ Exported {len(export_data['messages'])} messages")
        print(f"✅ Agent stats for {len(export_data['agent_stats'])} agents")
        
        # Show sample data
        if export_data['messages']:
            sample_msg = export_data['messages'][0]
            print(f"   Sample message: {sample_msg['message_id']} - {sample_msg['content'][:30]}...")
        
    except Exception as e:
        print(f"❌ Data export error: {e}")
    
    # Test 6: Admin interface commands
    print("\n6. Testing admin interface...")
    try:
        # Test message listing
        recent_messages = admin.list_messages(limit=5)
        print(f"✅ Listed {len(recent_messages)} recent messages")
        
        # Test status
        admin.show_status()
        
        # Mark first message as processed
        if message_ids:
            admin.mark_processed(message_ids[0])
            print(f"✅ Marked message {message_ids[0]} as processed")
        
    except Exception as e:
        print(f"❌ Admin interface error: {e}")
    
    # Test 7: Cleanup (optional)
    print("\n7. Cleanup test data (y/N):", end=" ")
    try:
        cleanup = input().strip().lower()
        if cleanup.startswith('y'):
            for msg_id in message_ids:
                admin.delete_message(msg_id)
            print(f"✅ Cleaned up {len(message_ids)} test messages")
        else:
            print("⏭️  Skipping cleanup - test data preserved")
    except:
        print("⏭️  Skipping cleanup")
    
    print("\n" + "=" * 50)
    print("🎉 Messages from Beyond System Test Complete!")
    print("\nNext steps:")
    print("1. Test with actual Claude API integration")
    print("2. Run admin interface: python admin_message_interface.py interactive")
    print("3. Add frontend integration to index.html")
    print("4. Deploy to VPS for production testing")


if __name__ == "__main__":
    asyncio.run(test_messages_system())