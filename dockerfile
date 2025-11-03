services:
  api:
    build: ./backend
    env_file: ./backend/.env
    ports: ["8000:8000"]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./backend/app/data:/app/app/data
  web:
    build: ./frontend
    environment:
      - VITE_API_URL=http://localhost:8000
    ports: ["5173:5173"]
    command: npm run dev -- --host
    depends_on: [api]
