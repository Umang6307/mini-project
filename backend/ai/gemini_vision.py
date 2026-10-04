"""
Multimodal Gemini Vision Diagnoser for Crop Health
Integrates with Gemini Vision API via standard library urllib.request.
Seamlessly falls back to OfflineFallbackManager when offline or unconfigured.
"""

import os
import json
import base64
import urllib.request
import urllib.error
from backend.config import Config
from backend.ai.offline_fallback import OfflineFallbackManager

fallback_engine = OfflineFallbackManager()

def analyze_crop_image(image_bytes: bytes, filename: str, crop: str, stage: str, symptoms: str = "") -> dict:
    api_key = Config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        print("[AI Diagnostic] No GEMINI_API_KEY detected. Utilizing OfflineFallbackManager.")
        result = fallback_engine.diagnose(crop, stage, symptoms, filename)
        return result

    try:
        mime_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            mime_type = "image/png"
        elif filename.lower().endswith(".webp"):
            mime_type = "image/webp"

        b64_image = base64.b64encode(image_bytes).decode('utf-8')

        prompt = f"""
You are an expert Indian plant pathologist. Analyze this leaf/crop image.
Crop: {crop}
Growth Stage: {stage}
Reported Symptoms: {symptoms}

Respond strictly with a JSON object conforming exactly to this schema:
{{
  "conditionName": "Specific disease or pest name (e.g. Yellow Stripe Rust)",
  "hindiName": "Hindi name of disease",
  "causalOrganism": "Scientific causal agent (e.g. Puccinia striiformis)",
  "severityLevel": "LOW or MEDIUM or HIGH or CRITICAL",
  "riskPct": 85,
  "visualSymptoms": ["symptom 1", "symptom 2", "symptom 3"],
  "chemicalTreatment": "Specific pesticide/fungicide formulation with dosage in Indian metrics (ml/g per litre or per acre)",
  "organicBioControl": "Biological/organic treatment (e.g. Trichoderma, Neem oil)",
  "estimatedCostInr": 650,
  "confidence": 0.95
}}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": b64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                raw_text = data['candidates'][0]['content']['parts'][0]['text']
                parsed = json.loads(raw_text)
                parsed["source"] = "gemini-vision"
                parsed["sourceLabel"] = "Gemini 2.5 Multimodal Vision AI"
                parsed["imageFilename"] = filename
                return parsed
            else:
                print(f"[AI Diagnostic] Gemini API status {response.status}. Using fallback.")
                return fallback_engine.diagnose(crop, stage, symptoms, filename)

    except Exception as e:
        print(f"[AI Diagnostic] Exception calling Gemini API ({e}). Seamlessly engaging OfflineFallbackManager.")
        return fallback_engine.diagnose(crop, stage, symptoms, filename)
