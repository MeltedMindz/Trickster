from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import asyncio
import json
import sqlite3
from datetime import datetime
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            message_json = json.dumps(message)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                if conn in self.active_connections:
                    self.disconnect(conn)


class ReligionStateManager:
    def __init__(self, db_path: str = "../religion_memory.db"):
        self.db_path = db_path
        
    def get_current_state(self) -> Dict:
        """Get current religion state from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get religion name
            cursor.execute("SELECT religion_name FROM religion_state WHERE id = 1")
            result = cursor.fetchone()
            religion_name = result['religion_name'] if result else None
            
            # Get recent doctrines
            cursor.execute("""
                SELECT content, proposed_by, accepted_at 
                FROM accepted_doctrines 
                ORDER BY accepted_at DESC 
                LIMIT 5
            """)
            doctrines = [dict(row) for row in cursor.fetchall()]
            
            # Get deities
            cursor.execute("SELECT name, domain, description FROM deities")
            deities = [dict(row) for row in cursor.fetchall()]
            
            # Get recent debates
            cursor.execute("""
                SELECT cycle_number, proposal_type, proposal_content, 
                       proposer, final_outcome, timestamp
                FROM debate_history 
                ORDER BY cycle_number DESC 
                LIMIT 10
            """)
            recent_debates = [dict(row) for row in cursor.fetchall()]
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) as count FROM debate_history")
            total_debates = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM accepted_doctrines")
            total_doctrines = cursor.fetchone()['count']
            
            conn.close()
            
            return {
                'religion_name': religion_name,
                'doctrines': doctrines,
                'deities': deities,
                'recent_debates': recent_debates,
                'statistics': {
                    'total_debates': total_debates,
                    'total_doctrines': total_doctrines
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error reading database: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_latest_debate(self) -> Optional[Dict]:
        """Get the most recent debate entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM debate_history 
                ORDER BY cycle_number DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            conn.close()
            
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting latest debate: {e}")
            return None


# Global instances
manager = ConnectionManager()
state_manager = ReligionStateManager()

# Shared state for orchestrator control
orchestrator_state = {
    "running": False,
    "paused": False,
    "cycle_count": 0
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("WebSocket server starting...")
    
    # Start background task to monitor database changes
    asyncio.create_task(monitor_database_changes())
    
    yield
    
    # Shutdown
    logger.info("WebSocket server shutting down...")


app = FastAPI(title="AI Religion Architects API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "AI Religion Architects WebSocket Server",
        "status": "running",
        "orchestrator": orchestrator_state,
        "connected_clients": len(manager.active_connections)
    }


@app.get("/api/state")
async def get_state():
    """Get current religion state"""
    return state_manager.get_current_state()


@app.get("/api/orchestrator/status")
async def get_orchestrator_status():
    """Get orchestrator status"""
    return orchestrator_state


@app.post("/api/orchestrator/pause")
async def pause_orchestrator():
    """Pause the orchestrator"""
    orchestrator_state["paused"] = True
    await manager.broadcast({
        "type": "control",
        "action": "paused",
        "timestamp": datetime.now().isoformat()
    })
    return {"status": "paused"}


@app.post("/api/orchestrator/resume")
async def resume_orchestrator():
    """Resume the orchestrator"""
    orchestrator_state["paused"] = False
    await manager.broadcast({
        "type": "control",
        "action": "resumed",
        "timestamp": datetime.now().isoformat()
    })
    return {"status": "resumed"}


@app.post("/api/prompt")
async def inject_prompt(prompt: Dict[str, str]):
    """Inject an external prompt into the debate"""
    if "content" not in prompt:
        raise HTTPException(status_code=400, detail="Missing 'content' field")
    
    # This would be connected to the orchestrator in production
    await manager.broadcast({
        "type": "external_prompt",
        "content": prompt["content"],
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "prompt_injected", "content": prompt["content"]}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        # Send initial state
        initial_state = state_manager.get_current_state()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "data": initial_state
        }))
        
        # Keep connection alive
        while True:
            # Wait for any message from client (ping/pong)
            data = await websocket.receive_text()
            
            # Echo back as pong
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def monitor_database_changes():
    """Monitor database for changes and broadcast updates"""
    last_debate_id = None
    db_path = Path("../religion_memory.db")
    
    while True:
        try:
            if db_path.exists():
                # Check for new debates
                latest_debate = state_manager.get_latest_debate()
                
                if latest_debate and latest_debate.get('id') != last_debate_id:
                    last_debate_id = latest_debate.get('id')
                    
                    # Broadcast the update
                    await manager.broadcast({
                        "type": "new_debate",
                        "data": latest_debate
                    })
                    
                    # Also broadcast updated state
                    current_state = state_manager.get_current_state()
                    await manager.broadcast({
                        "type": "state_update",
                        "data": current_state
                    })
                    
                    # Update orchestrator state
                    if latest_debate.get('cycle_number'):
                        orchestrator_state['cycle_count'] = latest_debate['cycle_number']
            
        except Exception as e:
            logger.error(f"Error monitoring database: {e}")
        
        # Check every second
        await asyncio.sleep(1)


async def broadcast_cycle_update(cycle_data: Dict):
    """Broadcast a cycle update to all connected clients"""
    await manager.broadcast({
        "type": "cycle_update",
        "data": cycle_data,
        "timestamp": datetime.now().isoformat()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")