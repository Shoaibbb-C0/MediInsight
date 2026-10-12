"""
Inline Nutrition Recommendation Engine for Simplifier 2.0.
Provides medically safe, culturally relevant (including familiar Indian food staples)
practical dietary guidance tailored to verified abnormal lab findings.
"""

from typing import List, Dict, Any, Optional

def generate_inline_nutrition(
    abnormal_biomarkers: List[Dict[str, Any]],
    patient_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates balanced, non-restrictive, everyday food ideas.
    Never prescribes extreme treatment diets or replaces clinical dietitian counsel.
    """
    diet_type = (patient_preferences or {}).get("dietary_preference", "omnivore") # 'vegetarian', 'vegan', 'omnivore'
    
    canonicals = {b.get("canonical_name") for b in abnormal_biomarkers}
    
    guidance_sections = []
    
    # 1. Glucose / HbA1c context
    if "glucose_fasting" in canonicals or "hba1c" in canonicals:
        foods_to_enjoy = [
            "Whole grains with high soluble fiber: steel-cut oats, brown rice, whole wheat roti, or broken wheat (daliya)",
            "Plant proteins & legumes: lentils (moong, masoor dal), chickpeas (chana), paneer or tofu, and edamame",
            "Colorful vegetables: spinach (palak), methi, okra (bhindi), bitter gourd (karela), and bell peppers",
            "Nuts and seeds: a small handful of almonds, walnuts, or chia seeds"
        ]
        gentle_adjustments = [
            "Enjoy meals with a balanced plate: half vegetables, one quarter protein, one quarter whole carbs",
            "Prefer whole fruits (apple, guava, berries) over strained fruit juices",
            "A short 10-15 minute walk after dinner supports natural muscle sugar uptake"
        ]
        guidance_sections.append({
            "topic": "Supporting Steady Blood Sugar",
            "why_relevant": "Your blood sugar or HbA1c readings are slightly elevated. Gentle daily food balance can help prevent sugar spikes.",
            "foods_to_enjoy": foods_to_enjoy,
            "everyday_tips": gentle_adjustments,
            "precautions": "Avoid drastic starvation diets or cutting all carbohydrates completely without doctor guidance."
        })

    # 2. Vitamin D context
    if "vitamin_d" in canonicals:
        guidance_sections.append({
            "topic": "Everyday Habits for Vitamin D & Bone Strength",
            "why_relevant": "Vitamin D levels were lower than optimal. While sunlight is the chief source, nutrition supports overall calcium utilization.",
            "foods_to_enjoy": [
                "Fortified milk, fortified plant milk, or curd/yogurt",
                "Egg yolks and mushrooms exposed to sunlight",
                "Sesame seeds (til) and leafy greens for synergistic calcium"
            ],
            "everyday_tips": [
                "Enjoy 15-20 minutes of mild early morning sunlight (before 10 AM) on arms or face",
                "Talk to your doctor regarding whether a short course of oral D3 drops is suitable"
            ],
            "precautions": "Food alone rarely replenishes significant vitamin D shortages; physician-guided supplementation is often most effective."
        })

    # 3. Cholesterol Context
    if "cholesterol_total" in canonicals:
        guidance_sections.append({
            "topic": "Heart-Friendly Everyday Choices",
            "why_relevant": "Total cholesterol was slightly elevated. Incorporating heart-healthy unsaturated fats supports healthy lipid profiles.",
            "foods_to_enjoy": [
                "Fiber-rich foods like oats, flaxseed powder, and apples",
                "Cooking with moderate cold-pressed mustard, olive, or groundnut oil instead of hydrogenated vanaspati",
                "Garlic, onions, and fresh seasonal vegetables"
            ],
            "everyday_tips": [
                "Limit deep-fried packaged snacks and processed pastries",
                "Stay well-hydrated throughout the day"
            ],
            "precautions": "If you have kidney or liver considerations, consult your physician before making major dietary adjustments."
        })

    # Fallback balanced wellness guidance if no specific abnormality
    if not guidance_sections:
        guidance_sections.append({
            "topic": "Everyday Balanced Nutrition",
            "why_relevant": "All tests appear within normal range. Maintaining everyday variety keeps your energy and organ functions steady.",
            "foods_to_enjoy": [
                "Plentiful fresh seasonal vegetables and local whole fruits",
                "Adequate protein from dals, dairy, beans, or lean sources",
                "Unrefined grains and wholesome pulses"
            ],
            "everyday_tips": [
                "Drink 2-3 liters of clean water daily",
                "Eat freshly cooked meals at regular intervals"
            ],
            "precautions": "Listen to your natural satiety cues and maintain comfortable daily movement."
        })

    return {
        "status": "ready",
        "sections": guidance_sections,
        "disclaimer": "These nutritional suggestions are for educational awareness and everyday wellness only. They do not constitute personalized clinical medical nutrition therapy."
    }
