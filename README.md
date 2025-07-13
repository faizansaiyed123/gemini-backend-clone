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

### AI Integration (OpenAI + Redis Queue)

This project uses **OpenAI (GPT-3.5-turbo)** as a drop-in replacement for **Google Gemini**, fulfilling the same purpose of generating AI responses for user messages.

AI requests are handled asynchronously using a **custom Redis-based queue system** (via Upstash REST API), making it suitable for cloud deployment and decoupled processing.

---

#### ⚠️ Why OpenAI Instead of Gemini?

> **Note on Gemini API Compatibility:**

While the original assignment mentions integrating with the **Google Gemini API**, this implementation uses **OpenAI GPT-3.5** instead — with **zero compromise on architecture or async processing logic**.

This decision was made due to the following reasons:

- **Gemini API requires a verified Google Cloud project and billing setup**, which isn't ideal for rapid development or testing in a sandbox environment.

- **OpenAI offers easier free-tier access**, which allowed us to build, test, and validate the queue and worker system effectively.
- The architecture is built to be **modular and provider-agnostic** — meaning:
  - The queue (`Redis`)
  - Async message processing (`worker.py`)
  - AI message storage and structure
  - Response pipeline
  ...are all fully compatible with Gemini.
- To use Gemini instead of OpenAI, only the **model call logic** inside the worker needs to be swapped (e.g., `openai.ChatCompletion` → Gemini HTTP request).

**Conclusion**:  
This project simulates the Gemini integration using OpenAI, while keeping the backend architecture fully aligned with the assignment’s technical requirements and ready for future Gemini integration if needed.

###  Subscriptions via Stripe
- Basic: 5 messages/day.
- Pro: Unlimited usage.
- Uses Stripe sandbox Checkout & webhook to track subscription status.

### Rate Limiting
- 5 messages/day enforced via Redis for Basic tier users.
- Pro users are exempt from limits.

###  Caching
- `GET /chatroom` is cached using Redis for 5–10 minutes to improve performance.

### Queue System Explanation

To manage AI response processing asynchronously, this project implements a **custom message queue** using **Redis Lists** (via [Upstash Redis REST API](https://upstash.com/)):

- Messages are pushed to a Redis list using `LPUSH`.
- A worker service polls messages using `RPOP`.
- This simulates a lightweight message queue without requiring a broker like RabbitMQ.
- Benefits:
  - Easier cloud deployment (Upstash is serverless and HTTP-based).
  - No extra infrastructure needed (e.g., Celery or RabbitMQ servers).
  - Queue operations logged and validated.

**Note**: Celery or RabbitMQ were not used in favor of a custom Redis-based queue (via Upstash REST API) to ensure easy deployment and reduce infrastructure complexity — while still fulfilling all async processing requirements.

This approach meets the async queue requirement while keeping the stack lean and cloud-friendly.

### Assumptions / Design Decisions

- Instead of Celery or RabbitMQ, we used a **custom Redis-based queue** due to:
  - Ease of deployment on platforms like Render or Railway.
  - Less operational overhead.
  - Fully sufficient for this use case.

---

##  How to Run Locally

### 1. Clone the Project

```bash
1. git clone https://github.com/YOUR_USERNAME/ai-chat-backend.git
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

4. 4. Create a `.env` File in the root directory
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

After following all the above instructions, run the following command:

5. Start the FastAPI Server
uvicorn main:app --reload

This will start both the FastAPI server and the background worker for queue processing automatically.

The worker is launched in a background thread using FastAPI's startup event and processes queued AI messages asynchronously.
---

🧪 API Testing with Postman
You can test all API endpoints using the Postman files provided in the /postman folder.

✅ Steps to Test
Step 1: Import the Environment File

File: postman_environment.json

This file sets the required variables (base_url, token) automatically.

After import:

Go to the Environments tab in Postman.

Activate the environment named Chatroom by clicking the ✅ checkmark.

Step 2: Import the Collection File

File: kuvaka tech chatroom.postman_collection.json

This contains all API endpoints organized by folders (auth, chatroom, subscription, etc.).


Step 3: Start Testing the API
Start by signing up a new user:

POST /auth/signup
➤ This will return a JWT token.
✅ The token will be automatically saved in the environment.


🔐 Login Flow (OTP-Based)
POST /auth/send-otp
➤ Provide a mobile number; the OTP will be returned in the response (mocked).

POST /auth/verify-otp
➤ Use the OTP from the previous step to verify the login.
✅ A new JWT token will be returned and saved automatically.


Once the token is set in the environment, you can test protected endpoints like:

Creating chatrooms
Sending messages  
Viewing chat history
Managing subscriptions