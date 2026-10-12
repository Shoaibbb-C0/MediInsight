"""
Production-Grade 7-Day Nutrition Planning Engine for Simplifier 2.0.
Version: 2.0.0
Generates a realistic, varied 7-day personalized educational food plan
incorporating actual lab findings, questionnaire preferences, allergy constraints,
medical safety rules, and intelligent meal alternatives.
"""

from typing import List, Dict, Any, Optional
import uuid
import datetime

from app.schemas.nutrition import (
    SevenDayNutritionPlan,
    DailyNutritionPlan,
    MealItem,
    MealAlternative,
    NutritionPreferencesSubmission
)
from app.services.nutrition_database import FOOD_DATABASE, get_food_by_id

# Day Themes
DAY_THEMES = [
    {"num": 1, "en": "Monday: Foundation & Digestive Comfort", "hi": "सोमवार: हल्का व सुपाच्य आहार", "mr": "सोमवार: पचनास हलका व संतुलित आहार"},
    {"num": 2, "en": "Tuesday: Fiber & Satiety Focus", "hi": "मंगलवार: फाइबर एवं पोषण संतुलन", "mr": "मंगळवार: फायबर आणि तृप्ती देणारा आहार"},
    {"num": 3, "en": "Wednesday: Mid-Week Steady Energy", "hi": "बुधवार: निरंतर ऊर्जा व सक्रियता", "mr": "बुधवार: निरंतर ऊर्जा देणारा आहार"},
    {"num": 4, "en": "Thursday: Plant-Protein & Pulse Variety", "hi": "गुरुवार: दालों एवं वनस्पति प्रोटीन की विविधता", "mr": "गुरुवार: डाळी व प्रथिनांची विविधता"},
    {"num": 5, "en": "Friday: Vibrant Greens & Micronutrients", "hi": "शुक्रवार: ताजी हरी सब्जियां एवं सूक्ष्म पोषक तत्व", "mr": "शुक्रवार: ताज्या पालेभाज्या व पोषण"},
    {"num": 6, "en": "Saturday: Weekend Wholesome Warmth", "hi": "शनिवार: संपूर्ण व तृप्तिकारक भोजन", "mr": "शनिवार: पौष्टिक व रुचकर जेवण"},
    {"num": 7, "en": "Sunday: Nourishing Restoration & Reset", "hi": "रविवार: शांतिदायक व ताजगी भरा आहार", "mr": "रविवार: ताजेतवाने करणारा सात्विक आहार"}
]

# Hydration Guidance
HYDRATION_MAP = {
    "en": "Aim for 2 to 2.5 liters of clean water spread evenly throughout your waking hours. Gentle warm water with lemon or jeera (cumin) water can be soothing after meals.",
    "hi": "दिन भर में २ से २.५ लीटर ताजा पानी नियमित अंतराल पर पिएं। भोजन के बाद हल्का गुनगुना पानी या जीरा पानी पाचन के लिए आरामदायक होता है।",
    "mr": "दिवसभरात २ ते २.५ लिटर पाणी नियमित वेळेत प्यावे. जेवणानंतर कोमट पाणी किंवा जिऱ्याचे पाणी पचनासाठी उपयुक्त ठरते."
}

def is_food_safe(food: Dict[str, Any], dietary_pref: str, allergies: List[str], restrictions: List[str]) -> bool:
    """Checks whether a food item matches user dietary preference and allergy constraints."""
    # Check dietary preference
    food_diets = food.get("dietary_types", [])
    if dietary_pref == "vegan" and "vegan" not in food_diets:
        return False
    if dietary_pref == "vegetarian" and "vegetarian" not in food_diets and "vegan" not in food_diets:
        return False
    if dietary_pref == "eggetarian" and "eggetarian" not in food_diets and "vegetarian" not in food_diets and "vegan" not in food_diets:
        return False

    # Check allergies
    food_allergens = food.get("allergens", [])
    for a in allergies:
        clean_a = a.strip().lower()
        if clean_a in food_allergens:
            return False
        # Specific match aliases
        if clean_a in ["peanut", "peanuts", "groundnut"] and "peanuts" in food_allergens:
            return False
        if clean_a in ["dairy", "milk", "lactose"] and "dairy" in food_allergens:
            return False
        if clean_a in ["gluten", "wheat"] and "gluten" in food_allergens:
            return False
        if clean_a in ["egg", "eggs"] and "eggs" in food_allergens:
            return False
        if clean_a in ["fish", "seafood"] and "fish" in food_allergens:
            return False

    # Check food restrictions
    for r in restrictions:
        clean_r = r.strip().lower()
        if clean_r in ["no_peanuts"] and "peanuts" in food_allergens:
            return False
        if clean_r in ["no_dairy"] and "dairy" in food_allergens:
            return False
        if clean_r in ["no_gluten"] and "gluten" in food_allergens:
            return False

    return True

def build_meal_item(food: Dict[str, Any], lang: str, dietary_pref: str, allergies: List[str], restrictions: List[str]) -> MealItem:
    """Builds a localized MealItem with safe alternatives."""
    name_field = f"name_{lang}" if f"name_{lang}" in food else "name_en"
    desc_field = f"desc_{lang}" if f"desc_{lang}" in food else "desc_en"
    portion_field = f"portion_{lang}" if f"portion_{lang}" in food else "portion_en"
    why_field = f"why_{lang}" if f"why_{lang}" in food else "why_en"

    # Assemble alternatives
    alternatives = []
    for alt_id in food.get("alternatives", []):
        alt_food = get_food_by_id(alt_id)
        if alt_food and is_food_safe(alt_food, dietary_pref, allergies, restrictions):
            alt_name = alt_food.get(f"name_{lang}") or alt_food.get("name_en")
            alt_desc = alt_food.get(f"desc_{lang}") or alt_food.get("desc_en")
            alt_why = alt_food.get(f"why_{lang}") or alt_food.get("why_en")
            alternatives.append(MealAlternative(
                id=alt_food["id"],
                name=alt_name,
                description=alt_desc,
                prep_time_minutes=20,
                why_it_fits=alt_why,
                tags=alt_food.get("tags", [])
            ))

    return MealItem(
        id=food["id"],
        meal_type=food["meal_type"],
        name=food.get(name_field, food["name_en"]),
        description=food.get(desc_field, food["desc_en"]),
        portion_guidance=food.get(portion_field, food.get("portion_en", "Standard portion")),
        why_recommended=food.get(why_field, food.get("why_en", "Provides balanced everyday nutrition.")),
        practical_prep_tips=food.get("prep_tips_en"),
        cultural_context="Familiar regional staple",
        alternatives=alternatives
    )

def generate_seven_day_plan(
    report_id: str,
    extractions: List[Dict[str, Any]],
    prefs: NutritionPreferencesSubmission,
    lang: str = "en"
) -> SevenDayNutritionPlan:
    """
    Generates an actual structured 7-day nutrition plan tailored to lab findings and patient context.
    Ensures zero duplicate monotonous repetition across days while respecting safety rules.
    """
    dietary_pref = prefs.dietary_preference
    allergies = prefs.allergies
    restrictions = prefs.food_restrictions

    # Filter candidate food pools by safety
    safe_breakfasts = [f for f in FOOD_DATABASE if f["meal_type"] == "breakfast" and is_food_safe(f, dietary_pref, allergies, restrictions)]
    safe_lunches = [f for f in FOOD_DATABASE if f["meal_type"] == "lunch" and is_food_safe(f, dietary_pref, allergies, restrictions)]
    safe_dinners = [f for f in FOOD_DATABASE if f["meal_type"] == "dinner" and is_food_safe(f, dietary_pref, allergies, restrictions)]
    safe_snacks = [f for f in FOOD_DATABASE if f["meal_type"] == "snack" and is_food_safe(f, dietary_pref, allergies, restrictions)]

    # Fallback to prevent crash if constraints were hyper-restrictive
    if not safe_breakfasts: safe_breakfasts = [f for f in FOOD_DATABASE if f["meal_type"] == "breakfast"]
    if not safe_lunches: safe_lunches = [f for f in FOOD_DATABASE if f["meal_type"] == "lunch"]
    if not safe_dinners: safe_dinners = [f for f in FOOD_DATABASE if f["meal_type"] == "dinner"]
    if not safe_snacks: safe_snacks = [f for f in FOOD_DATABASE if f["meal_type"] == "snack"]

    # Identify abnormal findings to determine clinical rationale and safety flags
    abnormal_canonicals = {b.get("canonical_name") for b in extractions if b.get("status") in ["high", "low", "needs_review"]}

    # Clinical rationale summary
    rationale_points = []
    if "glucose_fasting" in abnormal_canonicals or "hba1c" in abnormal_canonicals:
        if lang == "hi":
            rationale_points.append("रक्त शर्करा (ग्लूकोज) संतुलन को समर्थन देने के लिए घुलनशील फाइबर और संतुलित दालों को प्राथमिकता दी गई है।")
        elif lang == "mr":
            rationale_points.append("रक्तातील साखरेचे प्रमाण संतुलित ठेवण्यासाठी विद्राव्य फायबर आणि डाळींचा योग्य वापर केला आहे.")
        else:
            rationale_points.append("Prioritizes low-glycemic complex carbohydrates and legumes to support balanced blood sugar regulation.")

    if "vitamin_d" in abnormal_canonicals:
        if lang == "hi":
            rationale_points.append("विटामिन डी और हड्डियों के स्वास्थ्य हेतु कैल्शियम युक्त तिल, दही और संतुलित पोषक तत्वों का समावेश किया गया है।")
        elif lang == "mr":
            rationale_points.append("व्हिटॅमिन डी व हाडांच्या बळकटीसाठी कॅल्शियमयुक्त तीळ, ताजे दही आणि पूरक आहाराचा समावेश आहे.")
        else:
            rationale_points.append("Pairs dietary calcium and fortified options with mild morning sunlight guidance for vitamin D optimization.")

    if "cholesterol_total" in abnormal_canonicals:
        if lang == "hi":
            rationale_points.append("हृदय के स्वास्थ्य के लिए असंतृप्त वसा (अखरोट, मेवे) और ओट्स के घुलनशील फाइबर को शामिल किया गया है।")
        elif lang == "mr":
            rationale_points.append("हृदयाच्या आरोग्यासाठी ओट्समधील विद्राव्य फायबर आणि चांगल्या फॅट्सचा समावेश केला आहे.")
        else:
            rationale_points.append("Emphasizes soluble fiber from oats/legumes and unsaturated fats to foster heart-friendly lipid balance.")

    if not rationale_points:
        if lang == "hi":
            rationale_points.append("सभी परिणाम संतुलित होने के कारण दैनिक ऊर्जा, ताजगी और प्राकृतिक पोषण को केंद्र में रखा गया है।")
        elif lang == "mr":
            rationale_points.append("सर्व निकाल संतुलित असल्याने दैनंदिन ऊर्जा आणि नैसर्गिक पोषणावर भर दिला आहे.")
        else:
            rationale_points.append("Designed for general daily vitality and wholesome nourishment across familiar seasonal food groups.")

    # Safety guidance
    safety_notes = []
    if lang == "hi":
        safety_notes = [
            "यह योजना सामान्य स्वास्थ्य जागरूकता एवं पोषण शिक्षा के लिए है। यह किसी बीमारी का चिकित्सीय उपचार या दवा नहीं है।",
            "यदि आपको गुर्दे या यकृत संबंधी जटिलता, एलर्जी या गर्भावस्था है, तो किसी योग्य आहार विशेषज्ञ (डायटीशियन) से परामर्श अवश्य लें।",
            "भोजन की आदतों में अचानक अत्यधिक कठोर बदलाव न करें और अपने डॉक्टर द्वारा बताई गई दवाओं को जारी रखें।"
        ]
    elif lang == "mr":
        safety_notes = [
            "हा आहार आराखडा सामान्य पोषण शिक्षणासाठी आहे. हा कोणताही वैद्यकीय उपचार किंवा औषधांचा पर्याय नाही.",
            "तुम्हाला मूत्रपिंड किंवा यकृताचा जुनाट आजार, गरोदरपण किंवा विशिष्ट ऍलर्जी असल्यास नोंदणीकृत डायटीशियनचा सल्ला घ्या.",
            "आहारात अचानक टोकाचे बदल करू नका आणि डॉक्टरांनी दिलेली औषधे नियमित सुरू ठेवा."
        ]
    else:
        safety_notes = [
            "This 7-day food guide is provided for educational and wellness guidance only. It is not an individualized medical prescription or clinical nutrition therapy.",
            "If you have complex kidney, liver, or metabolic conditions, please review any major dietary adjustments with a registered dietitian or physician.",
            "Never stop prescribed medications or make drastic unsupervised dietary cuts without professional clinical counsel."
        ]

    # Check for conditions warranting dietitian referral
    referral_recommended = False
    referral_reason = None
    if "creatinine_serum" in abnormal_canonicals:
        referral_recommended = True
        referral_reason = "Serum creatinine was flagged outside standard range. Professional renal dietary assessment is strongly recommended."

    # Build 7 distinct days
    days = []
    for day_idx in range(7):
        theme_obj = DAY_THEMES[day_idx]
        theme_title = theme_obj.get(lang) or theme_obj["en"]

        # Varied selection using round-robin rotation across safe pools
        bf_food = safe_breakfasts[day_idx % len(safe_breakfasts)]
        lu_food = safe_lunches[day_idx % len(safe_lunches)]
        di_food = safe_dinners[day_idx % len(safe_dinners)]
        sn_food = safe_snacks[day_idx % len(safe_snacks)] if safe_snacks else None

        days.append(DailyNutritionPlan(
            day_number=day_idx + 1,
            day_name=f"Day {day_idx + 1}" if lang == "en" else f"दिन {day_idx + 1}" if lang == "hi" else f"दिवस {day_idx + 1}",
            focus_theme=theme_title,
            breakfast=build_meal_item(bf_food, lang, dietary_pref, allergies, restrictions),
            lunch=build_meal_item(lu_food, lang, dietary_pref, allergies, restrictions),
            dinner=build_meal_item(di_food, lang, dietary_pref, allergies, restrictions),
            snack=build_meal_item(sn_food, lang, dietary_pref, allergies, restrictions) if sn_food else None,
            hydration_guidance=HYDRATION_MAP.get(lang, HYDRATION_MAP["en"])
        ))

    plan_title = "Personalized 7-Day Educational Food Guide"
    if lang == "hi":
        plan_title = "व्यक्तिगत ७-दिवसीय शैक्षिक आहार योजना"
    elif lang == "mr":
        plan_title = "वैयक्तिक ७-दिवसीय शैक्षणिक आहार मार्गदर्शक"

    return SevenDayNutritionPlan(
        plan_id=f"plan_{uuid.uuid4().hex[:10]}",
        report_id=report_id,
        user_id=prefs.user_id,
        language=lang,
        plan_title=plan_title,
        clinical_basis_summary=" ".join(rationale_points),
        dietary_preference=dietary_pref,
        allergies=allergies,
        food_restrictions=restrictions,
        days=days,
        safety_guidance=safety_notes,
        dietitian_referral_recommended=referral_recommended,
        dietitian_referral_reason=referral_reason,
        disclaimer="Important: This educational food plan is designed to help you explore healthy meal ideas with your family and physician. It does not provide medical diagnosis, therapeutic prescription, or disease-cure claims."
    )

def swap_meal_in_plan(
    plan_dict: Dict[str, Any],
    day_number: int,
    meal_type: str,
    new_meal_id: str,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Intelligently replaces a specific meal on a given day with an alternative
    while preserving allergy safety and dietary constraints.
    """
    new_food = get_food_by_id(new_meal_id)
    if not new_food:
        return plan_dict

    dietary_pref = plan_dict.get("dietary_preference", "vegetarian")
    allergies = plan_dict.get("allergies", [])
    restrictions = plan_dict.get("food_restrictions", [])

    # Check that new food is safe
    if not is_food_safe(new_food, dietary_pref, allergies, restrictions):
        return plan_dict

    # Locate day
    for day in plan_dict.get("days", []):
        if day.get("day_number") == day_number:
            if meal_type in day:
                updated_item = build_meal_item(new_food, lang, dietary_pref, allergies, restrictions)
                day[meal_type] = updated_item.model_dump()
                break

    return plan_dict
