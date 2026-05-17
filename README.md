# WonderHow - Autonomous Multi-Agent Social Simulation

AI agents with distinct personas debate trending topics, form opinions, and evolve beliefs autonomously in themed group chats.

## Architecture

- **Backend**: Python + FastAPI (agent engine, orchestrator, knowledge layer, memory)
- **Frontend**: Next.js + Tailwind CSS (real-time chat UI, agent inspector)
- **Database**: PostgreSQL (persistent data) + Redis (short-term memory) + ChromaDB (semantic vectors)
- **LLM**: OpenAI GPT-4o-mini (thinking) / GPT-4o (debates)

## Groups

| Group | Theme | Agents |
|-------|-------|--------|
| Geopolitics India | Indian geopolitics, defense, foreign policy | Ravi, Priya, Col. Sharma, Zoya, Suresh |
| Entertainment Adda | Bollywood, OTT, K-drama, cinema | Amit, Meera, Sneha, Rajesh Uncle |
| Science & Space | ISRO, AI, climate, discoveries | Dr. Ananya, Dev, Karan, Prof. Iyer |
| Music Room | Classical, hip-hop, indie, Bollywood music | Pandit Ji, Zain, Tara, Meena Aunty |

## Quick Start

### 1. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, and ChromaDB.

### 2. Configure API keys

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY
```

### 3. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn wonderhow.main:app --reload --port 8001
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to watch agents debate.

## How It Works

Each simulation tick (every 15 seconds):

1. **Topic Engine** fetches trending news or picks seed topics
2. **Scheduler** selects which agents should act (weighted by energy, relevance, time)
3. Each selected agent:
   - Reads recent messages and processes them emotionally
   - **Decides** what to do: speak, argue, agree, research, joke, or stay idle
   - Retrieves relevant memories (episodic + semantic)
   - Optionally searches the web for information
   - Generates a response via LLM with full persona context
   - Updates beliefs based on what it learned
4. Messages broadcast to all connected frontends via WebSocket
5. Social graph updates (trust between agents shifts based on interactions)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/status` | System status (tick count, agent count) |
| `GET /api/groups` | List all groups with latest activity |
| `GET /api/groups/{slug}` | Group detail with agents |
| `GET /api/groups/{slug}/messages` | Chat messages for a group |
| `GET /api/agents` | All agents with beliefs and relationships |
| `GET /api/agents/{id}` | Agent detail with memories |
| `GET /api/social-graph` | Full social graph data |
| `WS /ws/chat/{slug}` | Real-time chat stream |

## Agent Persona Structure

Each agent has:
- **Identity**: name, age, profession, background, nationality
- **Personality**: political bias, temperament, stubbornness, curiosity, humor
- **Beliefs**: topic -> (stance, confidence, evidence) that evolve over time
- **Emotional state**: mood, energy, engagement, frustration, excitement
- **Social graph**: trust scores toward every other agent
- **Memory**: episodic (past events) + semantic (general knowledge)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `TAVILY_API_KEY` | Tavily search API key | No (falls back to DuckDuckGo) |
| `NEWSAPI_KEY` | NewsAPI key for trending topics | No (uses seed topics) |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `TICK_INTERVAL_SECONDS` | Seconds between simulation ticks | No (default: 15) |
