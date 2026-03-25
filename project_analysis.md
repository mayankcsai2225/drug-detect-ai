# 🛡️ NCB DrugNet Intelligence Platform - Documentation

The **NCB DrugNet Intelligence Platform** is a specialized OSINT (Open Source Intelligence) and AI-driven monitoring system designed for India's **Narcotics Control Bureau (NCB)** to detect, track, and deanonymize drug trafficking activity across public digital channels.

---

## 📖 1. Mission Overview
Drug traffickers increasingly use public channels on platforms like **Telegram**, **Instagram**, and **WhatsApp** to market substances, communicate prices, and coordinate drops.

This platform automates the "manual surveillance" traditionally done by intelligence officers by:
*   **Scanning** public channels 24/7.
*   **Classifying** content using AI to filter out noise from actual illegal activity.
*   **Extracting** actionable intelligence (phone numbers, crypto wallets, locations).
*   **Creating** court-ready evidence bundles automatically.

---

## 👥 2. User Persona: NCB Intelligence Officer
**Officer Vikram** is an intelligence specialist at the NCB Delhi Zonal Unit. He tracks several "Street-Level" and "Master" handles suspected of sourcing methamphetamines from cross-border channels.
*   **Need**: To know *when* a new shipment is announced without scrolling through thousands of messages.
*   **Need**: To identify the real phone number or Telegram ID of a distributor hiding behind a username.
*   **Need**: To generate a PDF report for legal action (NDPS Act).

---

## 🧪 3. User Stories

### A. Automatic Intelligence Discovery
> *“As an NCB Officer, I want to add a Telegram channel handle to the system so that it automatically scans for drug-related keywords and alerts me only if high-risk substance marketing is detected.”*

### B. Identity Deanonymization
> *“As an NCB Analyst, I want to see a map of connected phone numbers and crypto IDs found across different platforms, so I can link multiple accounts to a single individual or cartel.”*

### C. Court Evidence Generation
> *“As a Case Officer, I want to 'one-click export' a post into a PDF with its OCR text, metadata, and a SHA-256 integrity hash, so I can present it as digital evidence in court.”*

---

## 🛠️ 4. How to Use (Step-by-Step)

### Step 1: Initialize Targets
*   Go to the **"DISCOVERY & TARGETS"** tab.
*   Enter a Telegram channel link (e.g., `@drugnet_test`) or Instagram profile.
*   Set a **Scan Frequency** (e.g., Scan every 2 hours).
*   Click **"Add to Watchlist"**.

### Step 2: Monitoring the Live Feed
*   Open the **"LIVE DASHBOARD"**.
*   Watch the **"Intel Feed"** for real-time alerts. 
*   High-risk posts (based on AI classification) will show up with **Red indicators**.
*   Check the **"Risk Leaderboard"** to see which handles are currently the most active traffickers.

### Step 3: Deep OSINT & Mapping
*   Navigate to the **"OSINT IDENTITY MAP"**.
*   Select a Target Handle from the dropdown. 
*   The system will display a network graph showing every **Phone Number**, **Email**, **Crypto Wallet**, and **IP address** ever associated with that user.

### Step 4: Evidence Collection
*   Go to the **"EVIDENCE EXPLORER"** tab.
*   Paste a raw screenshot or post URL.
*   The system will automatically run **OCR (Optical Character Recognition)** to extract text and **Vision AI** to identify substance types (e.g., 'White powder', 'Pills').
*   Click **"Generate Evidence Bundle"** to download a finalized PDF report.

---

## ⚙️ 5. Technical Architecture

### 🧠 Stage 1: The NLP Pipeline
*   **Keyword Filtering**: Fast matching of 100+ NDPS-listed substances.
*   **Zero-Shot NLP**: Uses `distilbert-base-uncased` to classify the "intent" (e.g., Marketing, Personal Use, Recruitment).

### 🔍 Stage 2: The Scraper Engine
*   **Telegram (Telethon)**: Connects via API to stream public channel data anonymously.
*   **Instagram (Instaloader)**: Scrapes public profiles and bios for contact links.

### 🏠 Stage 3: The Evidence Core
*   **Vision AI (YOLOv8)**: Detects drug paraphernalia and substances in images.
*   **Encryption**: Every piece of intelligence is hashed using **SHA-256** to ensure it hasn't been tampered with before it reaches court.

---

## 🔒 6. Security and Compliance
*   **No Private Data**: This tool **only** accesses publicly available OSINT data.
*   **Encryption**: All sensitive intelligence in the database is protected by Supabase Row Level Security (RLS).
