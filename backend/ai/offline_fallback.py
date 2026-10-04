"""
Offline Fallback Manager for Crop Disease Diagnosis
Heuristic, rule-based agronomic inference engine that operates 100% offline
without requiring external cloud APIs or active internet connections.
"""

import json
from pathlib import Path
from backend.config import Config

class OfflineFallbackManager:
    def __init__(self):
        self.diseases = self._load_diseases()

    def _load_diseases(self):
        diseases_path = Config.DATA_DIR / 'diseases.json'
        if diseases_path.exists():
            try:
                with open(diseases_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading diseases.json: {e}")
        return []

    def diagnose(self, crop: str, stage: str = "", symptoms_text: str = "", image_filename: str = "") -> dict:
        crop_clean = crop.strip().lower()
        symptoms_clean = symptoms_text.strip().lower() if symptoms_text else ""
        stage_clean = stage.strip().lower() if stage else ""

        # Filter candidate diseases by crop (or All Crops)
        candidates = [
            d for d in self.diseases 
            if d.get("crop", "").lower() in crop_clean or crop_clean in d.get("crop", "").lower() or d.get("crop") == "All Crops"
        ]

        if not candidates:
            # Fallback to general leaf spot or first item
            candidates = self.diseases if self.diseases else []

        best_match = None
        best_score = -1

        for d in candidates:
            score = 0
            # Check stage matching
            stages = [s.lower() for s in d.get("stages", [])]
            if any(s in stage_clean or stage_clean in s for s in stages):
                score += 25

            # Check keywords in symptom text
            keywords = d.get("keywords", [])
            for kw in keywords:
                if kw in symptoms_clean:
                    score += 30

            # Check visual symptoms matching
            for vs in d.get("visualSymptoms", []):
                for word in vs.lower().split():
                    if len(word) > 4 and word in symptoms_clean:
                        score += 15

            if score > best_score:
                best_score = score
                best_match = d

        # If no explicit symptom matches, pick the top disease matching the crop & stage
        if not best_match or best_score <= 0:
            if candidates:
                best_match = candidates[0]
            else:
                best_match = {
                    "conditionName": "Generic Foliar Blight & Leaf Spot",
                    "causalOrganism": "Alternaria spp. / Helminthosporium spp.",
                    "severityLevel": "MEDIUM",
                    "riskPct": 65,
                    "visualSymptoms": ["Irregular chlorotic brown lesions", "Leaf tip dieback"],
                    "chemicalTreatment": "Mancozeb 75% WP @ 2g/L water spray",
                    "organicBioControl": "Neem Oil 1500 ppm @ 3ml/L + Cow urine 10%",
                    "estimatedCostInr": 450
                }

        confidence = 0.88 if best_score > 30 else 0.76

        return {
            "conditionName": best_match.get("conditionName"),
            "hindiName": best_match.get("hindiName", ""),
            "causalOrganism": best_match.get("causalOrganism", "Pathogenic Fungal Spore Complex"),
            "severityLevel": best_match.get("severityLevel", "HIGH"),
            "riskPct": best_match.get("riskPct", 80),
            "visualSymptoms": best_match.get("visualSymptoms", []),
            "chemicalTreatment": best_match.get("chemicalTreatment", ""),
            "organicBioControl": best_match.get("organicBioControl", ""),
            "estimatedCostInr": best_match.get("estimatedCostInr", 650),
            "confidence": confidence,
            "source": "offline-rule-engine",
            "sourceLabel": "Offline Demo / Rule-Based Analysis",
            "imageFilename": image_filename
        }
