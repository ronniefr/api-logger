# Reusable API Logger

**A modular middleware for tracking API requests in FastAPI (or similar)—logs method, path, timestamp, status, and more. Easy to plug into any project for quick debugging and monitoring.**

## 🚩 Why use this?

- Tracks essentials without bloating your code
- Reusable across APIs (e.g., integrate with your weather endpoint)
- Customizable levels (info/error) and outputs (console/file)
- Beginner-to-pro: Starts simple, scales to production monitoring
- Discussed alternatives like Express.js in code comments

## 🛠️ Features

- **Middleware Hook:** Intercepts requests/responses
- **Logging:** Method, path, time, status, duration
- **Modular:** Class-based for easy config/extension
- **Secure:** Avoids logging sensitive data by default

## 🚀 Quickstart

1. Clone:  

git clone git@github.com:ronniefr/api-logger.git
cd api-logger


2. Install dependencies:  

pip install fastapi uvicorn


3. Integrate & Run (example in FastAPI):  

from fastapi import FastAPI
from logger import LoggerMiddleware # Your middleware
app = FastAPI()
app.add_middleware(LoggerMiddleware)
uvicorn.run(app)

- Test with requests; check console/file logs.

## 🔑 Alternatives Discussion

- **Express.js (Node.js):** Simpler for JS stacks, but lacks FastAPI's async/type safety. Use if you're in MERN—code has notes on porting.

### ⚡ Example Log Output

[INFO] 2025-08-01T12:00:00 GET /weather/london - Status: 200 - Duration: 50ms


## 🤝 Contributing

- Fork and add features like DB logging or Express.js adapters!
- Open issues for integrations.

## 📄 License

MIT — free for all use cases!
