# AI Chat Backend (OpenAI-Powered)

This backend system is built with **FastAPI** to support AI chat functionality with OTP-based authentication, chatroom management, rate limiting, and Stripe-powered subscriptions.

Instead of Google Gemini, this implementation uses the **OpenAI API (GPT-3.5-turbo)** for generating AI responses.

---

##  Features

### OTP-Based Authentication
- Users login using mobile number + OTP (mocked, returned in API response).
- JWT-based auth system.
- Forgot/change password flows.

###  Chatroom Support
- Users can create and manage multiple chatrooms.
- Conversations are stored in the database.
- AI responses are processed via a **Redis-based async queue**.

###  AI Integration (OpenAI)
- Uses `openai.ChatCompletion` to get GPT-3.5-turbo replies.

###  Subscriptions via Stripe
- Basic: 5 messages/day.
- Pro: Unlimited usage.
- Uses Stripe sandbox Checkout & webhook to track subscription status.

### Rate Limiting
- 5 messages/day enforced via Redis for Basic tier users.
- Pro users are exempt from limits.

###  Caching
- `GET /chatroom` is cached using Redis for 5–10 minutes to improve performance.

---

##  How to Run Locally

### 1. Clone the Project

```bash
git clone https://github.com/YOUR_USERNAME/ai-chat-backend.git
cd ai-chat-backend


2. Set Up Virtual Environment & Install Dependencies
# Create and activate virtual environment
python -m venv venv

# Activate:
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt


3. Set Up PostgreSQL and Redis
Ensure PostgreSQL is installed and a database is created.
Ensure Redis is installed and running locally on localhost:6379.

4. Create a .env File
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/gemini

# JWT
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
GMAIL_USERNAME=your_email@gmail.com
GMAIL_PASSWORD=your_app_password

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis (Upstash or Local)
UPSTASH_REDIS_REST_URL=your_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token
REDIS_URL=redis://localhost:6379

# Stripe (Sandbox)
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
STRIPE_PRICE_ID=your_stripe_price_id

# Misc
PORT=8000
SERVER_TIMEOUT=200



5. Start the FastAPI Server
uvicorn main:app --reload


6. Start the Background Worker
python -m src.services.worker
