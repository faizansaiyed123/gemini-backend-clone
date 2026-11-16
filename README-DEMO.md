# Gemini Backend Clone — Demo Mode

This branch contains an isolated recruiter demo API. It preserves the existing frontend-facing route names and response envelope while replacing external infrastructure with deterministic in-memory behavior.

## Run locally

    python -m pip install -r requirements.txt
    uvicorn demo_api:app --host 0.0.0.0 --port 8000

Health check: GET /health

## Demo sign-in

- Mobile: 9876543210
- OTP: 246810
- Password for the seeded account: DemoPass123!

The sign-in code is intentionally fixed and visible in the OTP API response in this demo only. Signup also works with any unused 10–15 digit mobile number.

## Included workflows

- OTP sign-in, signup, and password recovery
- Current-user profile and password change
- Chatroom creation, listing, and history
- Message submission with a delayed in-memory assistant reply
- Five-message Basic daily limit and simulated Pro upgrade
- Ownership checks and invalid-auth handling

Assistant responses are deterministic templates. They do not call Gemini, OpenAI, or another model.

## Isolation and safety

demo_api.py is a separate entry point and does not import app.py, production settings, database helpers, SQLAlchemy tables, Redis queue code, worker code, OpenAI, or Stripe. State is synthetic and process-local; restarting the process resets it. The simulated Pro endpoint does not collect payment or contact Stripe.

Run the demo tests with:

    PYTHONPATH=. pytest -q demo_tests

This branch is for demonstration only. It is not a production backend or a persistent multi-user service.
