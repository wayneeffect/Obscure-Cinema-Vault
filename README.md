# 🎬 Obscure Cinema Vault

A lightweight, production-hardened web application designed to help film enthusiasts discover hidden cinematic gems. Instead of pushing mainstream blockbusters, this engine inverts traditional recommendation algorithms to surface high-rated, long-tail movies with low vote counts.

Live application deployed on **Render**.

---

## ✨ Features

* **Obscurity Engine:** Filters the TMDB library to isolate movies with strong ratings ($\ge 6.8/10$) and low vote volume ($\le 500$ votes).
* **Randomized Archeology:** Dynamically cycles through search pages to yield fresh recommendations on every query.
* **Resilient UX:** Handles missing movie posters, null descriptions, and network timeouts with graceful fallback states.
* **Production-Hardened Security:** Built-in rate limiting, Content Security Policy (CSP) headers, and server-side API proxying to keep credentials private.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, Gunicorn
* **Security & Middleware:** Flask-Limiter (Rate Limiting), Flask-Talisman (Security Headers)
* **API:** [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API)
* **Deployment:** Render (PaaS) + GitHub Integration

---

## 🏗️ Architecture & Security

To prevent client-side abuse and protect private credentials, the frontend **never communicates directly with TMDB**. 

```text
[ Browser / Frontend ] 
         │  
         ▼ GET /api/pick-movie (Rate-Limited: 15 req/min)
[ Flask Proxy Server ] 
         │  
         ▼ GET /discover/movie (Appends Secret TMDB_API_KEY)
[ TMDB API Engine ]

```

---

## 🚀 Local Development Setup

### 1. Prerequisites

* Python 3.10+
* A free API key from [The Movie Database (TMDB)](https://www.themoviedb.org/)

### 2. Installation & Run

1. **Clone the repository:**
```bash
git clone [https://github.com/your-username/obscure-cinema-vault.git](https://github.com/your-username/obscure-cinema-vault.git)
cd obscure-cinema-vault

```


2. **Create and activate a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Set your environment variable and start the application:**
```bash
export TMDB_API_KEY="your_tmdb_api_key_here"  # On Windows PowerShell: $env:TMDB_API_KEY="your_tmdb_api_key_here"
python app.py

```


5. Open `http://localhost:5000` in your browser.

---

## 📦 Deploying to Render

1. Push this repository to **GitHub**.
2. Log into **Render** and create a **New Web Service** connected to your repo.
3. Configure the runtime settings:
* **Runtime:** `Python 3`
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn --workers 2 --threads 2 --timeout 30 app:app`


4. Under **Environment**, add the secret variable:
* **Key:** `TMDB_API_KEY`
* **Value:** `<Your TMDB API Key>`


5. Click **Deploy**.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

```

```
