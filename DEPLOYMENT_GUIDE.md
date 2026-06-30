# JARVIS AI OS - Deployment & Packaging Guide

This guide details steps to deploy and package JARVIS AI OS on a production Windows environment.

---

## 📋 Prerequisites

* **Operating System**: Windows 10 or Windows 11 (64-bit).
* **Python**: v3.11 or later.
* **Node.js**: v18.0 or later (with npm).
* **Tesseract OCR**: (Optional, for visual OCR) Installed and added to system PATH.

---

## 🛠️ Step-by-Step Installation

### 1. Initialize Python Backend
Create a virtual environment and install standard requirements:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Electron HUD Frontend
Compile Vite packages and build Vite production output files:
```powershell
cd jarvis-ui
npm install
npm run build
```

### 3. Setup Configurations
Copy `.env.example` to `.env` and set active provider API keys:
```powershell
copy .env.example .env
```

---

## 📦 Packaging & Bundling

To compile JARVIS into a single installer setup executable, run the packaging builder script:
```powershell
python package_jarvis.py
```

The script audits:
1. Environment configurations (`.env`).
2. Dependency files (`requirements.txt`).
3. Frontend compiled assets directory structure.
4. Output installer packages saved inside the `release/` folder.

---

## 🔄 Updates Deployment

Deploy updates by updating the version manifest file `manifest.json` on the update server. The manifest format must include:
* `latest_version`: SemVer string (e.g. `1.0.1`).
* `signature`: cryptographic signature checksum format `SHA256:<checksum>`.
* `delta_url`: delta update patch zip URL.
