# 🚀 Hugging Face Deployment Plan: NCB DrugNet Platform

This document outlines the step-by-step process for deploying the NCB DrugNet Intelligence Platform to Hugging Face (HF) Spaces as a Docker-based application.

## 1. Prerequisites
- [ ] A [Hugging Face](https://huggingface.co/join) account.
- [ ] A [Supabase](https://supabase.com/) project (Free Tier).
- [ ] [Telegram API](https://my.telegram.org) credentials.
- [ ] Optional: Instagram session data (for deeper IG scans).

## 2. Setting Up the Hugging Face Space
1. Go to **Hugging Face → New Space**.
2. **Space Name:** `ncb-drugnet` (or your preferred name).
3. **Select SDK:** Choose **Docker**.
4. **License:** Select appropriate (e.g., `MIT`).
5. **Space Hardware:** Use **CPU basic** (Free) or **T4 small** (if you want faster image processing).
6. **Visibility:** Public or Private.
7. Click **Create Space**.

## 3. Configuring Secrets (Crucial)
Your app depends on sensitive environment variables. Add these in **Settings → Variables and Secrets → New Secret**:

| Secret Name | Purpose |
| :--- | :--- |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase `anon` public key |
| `SUPABASE_SERVICE_KEY` | Your Supabase `service_role` key (needed for demo data inserts) |
| `HUGGINGFACE_API_TOKEN` | For token-based access to HF Hub models (optional) |
| `TELEGRAM_API_ID` | Your Telegram App api_id from `my.telegram.org` |
| `TELEGRAM_API_HASH` | Your Telegram App api_hash from `my.telegram.org` |

## 4. Repository Preparation
The following files are already optimized for deployment in your local directory:

- **`Dockerfile`**: Configured with a non-root user (UID 1000) and port `7860`.
- **`requirements.txt`**: Complete dependency list including `torch`, `uvicorn`, and `gradio`.
- **`app/main.py`**: Properly mounts Gradio into FastAPI and uses environment variables.

### Large Files Checklist
- [x] **`yolov8n.pt`** (6.5 MB): Small enough to be pushed directly via Git.
- [ ] **LFS Check:** If you add larger models (e.g., YOLOv8-large), ensure you initialize Git LFS:
  ```bash
  git lfs install
  git lfs track "*.pt"
  ```

## 5. Initial Deployment (via Git)
1. **Clone the Space:**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/ncb-drugnet
   ```
2. **Sync Files:** Copy all files from `c:\drug_detect` to the cloned directory (excluding `.venv`, `.git`, and sensitive logs).
3. **Commit and Push:**
   ```bash
   git add .
   git commit -m "Initial deployment of NCB DrugNet"
   git push
   ```

## 6. Verification and Troubleshooting
1. **Logs View:** Monitor the "Logs" tab on your HF Space to watch the Docker build and startup process.
2. **Health Check:** Your Space should be available at `https://huggingface.co/spaces/YOUR_USERNAME/ncb-drugnet`.
3. **Common Pitfalls:**
   - **Permission Errors:** The `Dockerfile` must use `useradd -m -u 1000 user` because HF restricts root access.
   - **Port Conflicts:** Ensure `EXPOSE 7860` and the `uvicorn` command matches port `7860`.
   - **Database Connectivity:** If you see "Supabase Connection Failed," double-check that your secrets don't have leading/trailing spaces.

## 7. Future Enhancements
- **Persistent Storage:** To save local logs or PDF exports permanently, consider mounting a [HF Dataset as Persistent Storage](https://huggingface.co/docs/hub/spaces-storage).
- **GPU Acceleration:** Switch to "T4 Small" in settings to significantly speed up YOLOv8 and OCR processing.
