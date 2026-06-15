# 🚀 Advanced Persian Text OCR & Structured JSON Extraction Pipeline

An enterprise-grade, multi-modal Vision-AI web application designed to intelligently detect, segment, and extract structured key-value data from Persian and English forms/documents without relying on strict structural delimiters like colons (`:`).

---

## ✨ Key Features

* **Layout-Aware Key-Value Extraction:** Leverages advanced vision-language models (Gemini 2.5 Flash) to understand form layouts, bounding boxes, and field boundaries dynamically.
* **Strict Language Preservation:** Guarantees no automatic translations; Persian keys/values remain Persian, and English text remains English.
* **Smart Filtering:** Automatically ignores isolated words, page titles, or scattered text guidelines that do not belong to a real key-value pair.
* **Live Image Preview Dashboard:** A sleek, modern UI built with Tailwind CSS and the elegant Vazirmatn Persian typeface, allowing users to drop images and see immediate structural previews.
* **SQLite Analytics Endpoint (`/stats`):** Automatically tracks and persists AI confidence scores, serving real-time system metrics (Average Accuracy %, total documents processed) via a pretty-printed JSON dashboard.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Flask-CORS
* **AI Core:** Google GenAI SDK (Gemini 2.5 Flash Multimodal)
* **Database:** SQLite (Lightweight, zero-config local storage)
* **Frontend:** HTML5, JavaScript (Fetch API), Tailwind CSS

---

## 🚀 Quick Start

### 1. Prerequisites & Installation
Ensure you have Python installed, then clone this repository and install the dependencies:
```bash
pip install google-genai pillow flask flask-cors
