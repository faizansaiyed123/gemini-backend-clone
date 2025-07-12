CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mobile VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    otp_code VARCHAR(6),
    otp_created_at TIMESTAMP,
    password_hash TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(10) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
