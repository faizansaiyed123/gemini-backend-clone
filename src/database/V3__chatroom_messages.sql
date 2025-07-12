CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY,
    chatroom_id UUID REFERENCES chatrooms(id) ON DELETE CASCADE,
    sender TEXT NOT NULL, -- 'user' or 'gemini'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
