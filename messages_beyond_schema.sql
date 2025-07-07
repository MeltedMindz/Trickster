-- Messages from Beyond Database Schema
-- A system for admin-controlled external messages that agents interpret

-- Table 1: External messages that agents receive and interpret
CREATE TABLE messages_from_beyond (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,  -- Unique identifier for each message
    timestamp TIMESTAMP NOT NULL,      -- When message was inputted
    content TEXT NOT NULL,             -- Clean text content of the message
    source_label TEXT DEFAULT 'Beyond', -- Label for message source (e.g., "Beyond", "The Void", "Cosmos")
    cycle_number INTEGER,              -- Cycle when message was received
    admin_notes TEXT,                  -- Optional admin notes about the message
    processed BOOLEAN DEFAULT FALSE,   -- Whether agents have reflected on this message
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Agent reflections on external messages
CREATE TABLE message_reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,          -- Reference to messages_from_beyond.message_id
    agent_id TEXT NOT NULL,            -- Agent name (Zealot, Skeptic, Trickster)
    reflection_text TEXT NOT NULL,     -- Agent's interpretation/reflection
    sentiment_score REAL,              -- Emotional response (-1.0 to 1.0)
    theological_impact TEXT,           -- How this affects their beliefs
    confidence_change REAL DEFAULT 0.0, -- Change in belief confidence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
);

-- Table 3: Group discussions about messages
CREATE TABLE message_discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,          -- Reference to messages_from_beyond.message_id
    discussion_round INTEGER NOT NULL, -- Round number in the discussion
    agent_id TEXT NOT NULL,            -- Speaking agent
    response_text TEXT NOT NULL,       -- Agent's contribution to discussion
    response_type TEXT DEFAULT 'interpretation', -- 'interpretation', 'question', 'challenge', 'agreement'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
);

-- Table 4: Cultural/doctrinal changes triggered by messages
CREATE TABLE message_influences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,          -- Reference to messages_from_beyond.message_id
    influence_type TEXT NOT NULL,      -- 'doctrine_shift', 'ritual_change', 'belief_update', 'relationship_change'
    description TEXT NOT NULL,         -- Description of the change
    agent_affected TEXT,               -- Which agent was primarily affected
    magnitude REAL DEFAULT 0.5,       -- Strength of influence (0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
);

-- Table 5: Message processing status and metadata
CREATE TABLE message_processing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT UNIQUE NOT NULL,   -- Reference to messages_from_beyond.message_id
    reflection_phase_complete BOOLEAN DEFAULT FALSE,
    discussion_phase_complete BOOLEAN DEFAULT FALSE,
    influence_analysis_complete BOOLEAN DEFAULT FALSE,
    total_agent_responses INTEGER DEFAULT 0,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
);

-- Indexes for performance
CREATE INDEX idx_messages_timestamp ON messages_from_beyond(timestamp);
CREATE INDEX idx_messages_processed ON messages_from_beyond(processed);
CREATE INDEX idx_reflections_message ON message_reflections(message_id);
CREATE INDEX idx_discussions_message ON message_discussions(message_id);
CREATE INDEX idx_influences_message ON message_influences(message_id);
CREATE INDEX idx_processing_message ON message_processing(message_id);