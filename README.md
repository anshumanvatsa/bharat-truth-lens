<div align="center">

# 🇮🇳 Pulse of India

### AI-Powered Fake News Detection & Civic Engagement Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![DistilBERT](https://img.shields.io/badge/DistilBERT-Fine--tuned-FF6B35?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com/atlas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**A hybrid NLP system combining fine-tuned DistilBERT + Wikipedia evidence retrieval + semantic similarity + source credibility weighting — built for Indian political claim verification. With a full civic platform: real-time voting, politician tracking, and media decay analysis.**

[🌐 Live Demo](#deployment) · [📖 Research Results](#evaluation-results) · [🚀 Quick Start](#quick-start) · [🏗️ Architecture](#architecture)

</div>

---

## 🏆 What We Achieved

> This project was built from scratch, benchmarked on real datasets, and represents multiple iterations of improvement across ML, backend, and frontend.

### ⚡ Research-Grade NLP Pipeline
- **Fine-tuned DistilBERT** on LIAR dataset (6-class political misinformation)
- **4-layer hybrid pipeline** ablation-studied on **500 FEVER benchmark samples**
- **+7.9% Macro F1** improvement from baseline (V-A) to full hybrid (V-D)
- **Bootstrap confidence intervals** (n=1,000) and McNemar significance testing
- **Dynamic severity scoring** across 4 civic dimensions (economic/social/political/national)

### 🗳️ Real Civic Voting System
- **One person, one vote** — enforced at database level (MongoDB unique user_id)
- **All 28 States + 8 Union Territories** of India
- **Age-wise vote breakdown** (18-25 / 26-40 / 41-60 / 60+) — live, real-time
- **State-wise leading candidate** — updates instantly as votes come in
- **JWT authentication** — secure, token-based, 24-hour sessions

### 🔥 Full-Stack Excellence
- **Groq API (LLaMA-3.1-8B)** — cloud LLM for AI reasoning, no 4.69GB model needed in production
- **Wikipedia + Tavily** dual evidence retrieval
- **Source credibility weighting** — Wikipedia (0.95) > unknown (0.50)
- **Production-ready** — deployed on Vercel (frontend) + Railway (backend)

---

## 📊 Evaluation Results

### Ablation Study — FEVER Dataset (500 samples)

| Variant | Description | Accuracy | Macro F1 | Δ Acc | Δ F1 |
|---------|-------------|:--------:|:--------:|:-----:|:----:|
| V-A | DistilBERT only (baseline) | 0.512 | 0.4705 | — | — |
| V-B | + Evidence retrieval | 0.544 | 0.5433 | +0.032 | +0.073 |
| V-C | + Semantic similarity (additive) | 0.548 | 0.5463 | +0.036 | +0.076 |
| **V-D** | **+ Source credibility (Full Hybrid)** | **0.552** | **0.5499** | **+0.040** | **+0.079** |

### Bootstrap Confidence Intervals (n=1,000)

| Metric | 95% CI Lower | 95% CI Upper |
|--------|:-----------:|:-----------:|
| Macro F1 gain | 0.0399 | 0.1197 |
| F1-True gain | 0.1434 | 0.2520 |
| Accuracy gain | 0.000 | 0.080 |

> McNemar test: χ² = 3.41, p = 0.065 (marginally significant — disclosed transparently in limitations)

---

## 🌐 Pages & Feature Status

| Page | Status | Description |
|------|--------|-------------|
| 🏠 **Home** | ✅ Live | Hero dashboard with animated civic metrics |
| 🔍 **AI Analyzer** | ✅ Live — Real Backend | DistilBERT + evidence + LLaMA-3 explanations |
| 🗳️ **Election Pulse** | ✅ Live — Real Voting | PM opinion poll, one-person-one-vote, all states, age breakdown |
| 🔐 **Login / Signup** | ✅ Live — JWT Auth | MongoDB-backed, secure, age + state collected at signup |
| 🗳️ **Public Pulse** | 🔧 In Development | Civic issue voting — hardcoded sample data, real API coming |
| 📰 **Trending Cases** | 🔧 In Development | Case tracker — curated static data, live feed coming |
| 👤 **Leaders** | 🔧 In Development | Politician profiles — sample data, real scraping coming |

> Pages marked **🔧 In Development** are functional UI demos with curated data. They are intentional prototypes showing the product vision — live data integrations are planned for the next release.

---

## 🏗️ Architecture

```
                     ┌─────────────────────────────────────────┐
                     │           Input Claim (text)            │
                     └──────────────────┬──────────────────────┘
                                        │
                     ┌──────────────────▼──────────────────────┐
                     │   Layer 1: DistilBERT Classifier         │
                     │   Fine-tuned on LIAR (6-class → binary) │
                     │   Output: base_pred + confidence         │
                     └──────────────────┬──────────────────────┘
                                        │
               ┌────────────────────────▼────────────────────────┐
               │         Layer 2: Evidence Retrieval              │
               │  Wikipedia REST API  +  Tavily Search API        │
               │  2-stage lookup, entity extraction, top-6 docs  │
               └────────────────────────┬────────────────────────┘
                                        │
               ┌────────────────────────▼────────────────────────┐
               │         Layer 3: Semantic Scoring                │
               │  all-MiniLM-L6-v2 (384-dim cosine similarity)   │
               │  Source credibility weights:                     │
               │    Wikipedia(0.95) > BBC/Reuters(0.92) > (0.50) │
               └────────────────────────┬────────────────────────┘
                                        │
               ┌────────────────────────▼────────────────────────┐
               │         Layer 4: Hybrid Override Engine          │
               │  Condition A: conf < 0.80 AND |signal| > 0.08   │
               │  Condition B: avg_sim > 0.55 AND conf < 0.90    │
               └────────────────────────┬────────────────────────┘
                                        │
               ┌────────────────────────▼────────────────────────┐
               │      LLaMA-3 Explanation (Groq API)             │
               │  Dynamic severity: economic/social/political/    │
               │  national — computed from 80+ keywords          │
               └─────────────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
pulseofindia-main/
│
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app + CORS
│   │   ├── config.py               # Pydantic settings
│   │   ├── database.py             # MongoDB (Motor async)
│   │   ├── routers/
│   │   │   ├── analyze.py          # POST /analyze/ — AI fact-check
│   │   │   ├── auth.py             # POST /auth/signup, /auth/login
│   │   │   └── vote.py             # POST /vote/pm — real voting API
│   │   ├── schemas/auth.py         # Pydantic schemas (age_group, state)
│   │   ├── services/
│   │   │   ├── analyzer.py         # 🧠 Core hybrid pipeline (V-D)
│   │   │   └── llama_reasoner.py   # Groq/LLaMA explanation engine
│   │   └── utils/auth.py           # JWT, bcrypt, OAuth2
│   ├── ablation_study.py           # Full ablation (V-A → V-D on FEVER)
│   ├── liar_eval.py                # LIAR dataset evaluation + figures
│   ├── requirements.txt
│   ├── railway.toml                # Railway deployment
│   ├── Procfile                    # Heroku/Render deployment
│   └── .env.example
│
├── ml/                             # ML research pipeline
│   ├── models/liar_model/          # Fine-tuned DistilBERT*
│   ├── scripts/train_liar_model.py # Training script
│   ├── bootstrap_ci.py             # Bootstrap confidence intervals
│   └── bootstrap_results_real.json
│
└── pulseofindia-main/              # React frontend (Vite + TypeScript)
    ├── src/
    │   ├── lib/api.ts              # Shared API client (auth + voting)
    │   ├── pages/
    │   │   ├── AnalyzerPage.tsx    # 🔍 AI Analyzer (live)
    │   │   ├── ElectionPulsePage.tsx # 🗳️ Real voting (live)
    │   │   ├── LoginPage.tsx       # 🔐 JWT login (live)
    │   │   ├── SignUpPage.tsx      # 📝 Signup w/ age+state (live)
    │   │   ├── PublicPulsePage.tsx # 🔧 In development
    │   │   ├── TrendingPage.tsx    # 🔧 In development
    │   │   └── LeadersPage.tsx     # 🔧 In development
    │   └── components/
    ├── vercel.json                 # Vercel SPA deployment
    └── .env.example
```

> *Model weights excluded from git. See [Model Weights](#quick-start) section.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+, Node.js 18+, MongoDB (local or Atlas)
- [Groq API key](https://console.groq.com) — free, replaces 4.69GB local LLaMA
- [Tavily API key](https://tavily.com) — free tier (1,000 searches/month)

### 1. Clone

```bash
git clone https://github.com/anshumanvatsa/bharat-truth-lens.git
cd bharat-truth-lens
```

### 2. Backend

```bash
cd backend
python -m venv venv && venv\Scripts\activate   # Windows
# source venv/bin/activate                      # macOS/Linux
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY, TAVILY_API_KEY, MONGODB_URL
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd pulseofindia-main
npm install
cp .env.example .env.local   # leave VITE_API_URL empty for local dev
npm run dev
```

Frontend: `http://localhost:5173`

### 4. Model Weights

DistilBERT weights are too large for git. Place your trained model at:
```
ml/models/liar_model/
```
Required files: `config.json`, `model.safetensors`, `tokenizer.json`, `vocab.txt`

To train from scratch: `cd ml/scripts && python train_liar_model.py`

---

## 🌐 Deployment

### Frontend → Vercel (Free)

1. Import repo at [vercel.com](https://vercel.com) → Root Directory: `pulseofindia-main`
2. Add env var: `VITE_API_URL = https://your-backend.railway.app`
3. Deploy ✅

### Backend → Railway (Free)

1. Import repo at [railway.app](https://railway.app) → Root Directory: `backend`
2. Add env vars from `.env.example`
3. Railway auto-reads `railway.toml` ✅

### After Deploy

Add your Vercel URL to `backend/app/main.py` CORS origins:
```python
"https://bharat-truth-lens.vercel.app",
```

---

## 🔌 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/analyze/` | None | AI fact-check a claim |
| POST | `/auth/signup` | None | Register with age + state |
| POST | `/auth/login` | None | Get JWT token |
| GET | `/auth/me` | Bearer | Get current user profile |
| POST | `/vote/pm` | Bearer | Cast PM vote (one per user) |
| GET | `/vote/pm/results` | None | Live results by age + state |
| GET | `/vote/pm/my-vote` | Bearer | Check if user has voted |
| GET | `/vote/pm/candidates` | None | List all PM candidates |
| GET | `/vote/states` | None | All Indian states + UTs |
| GET | `/health` | None | Health check |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | DistilBERT fine-tuned on LIAR (HuggingFace) |
| Embeddings | all-MiniLM-L6-v2 (SentenceTransformers) |
| LLM Reasoning | Groq API (LLaMA-3.1-8B-Instant) |
| Evidence | Wikipedia REST API + Tavily Search |
| Backend | FastAPI + Uvicorn + Motor (async MongoDB) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Database | MongoDB Atlas |
| Frontend | React 18 + TypeScript + Vite |
| UI | shadcn/ui + Radix UI + Tailwind CSS |
| Charts | Recharts |
| Animations | Framer Motion |

---

## 📋 Citation

```bibtex
@misc{pulseofindia2026,
  title  = {Pulse of India: Hybrid NLP for Indian Political Claim Verification},
  author = {Vatsa, Anshuman},
  year   = {2026},
  url    = {https://github.com/anshumanvatsa/bharat-truth-lens}
}
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

<div align="center">

Made with ❤️ for Indian democracy · Truth. Transparency. Accountability.

⭐ **Star this repo** if it helped you!

</div>
