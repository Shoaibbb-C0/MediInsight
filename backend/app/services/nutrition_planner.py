"""
Production-Grade 7-Day Nutrition Planning Engine for Simplifier 2.0.
Version: 2.0.0
Generates a realistic, varied 7-day personalized educational food plan
incorporating actual lab findings, questionnaire preferences, allergy constraints,
medical safety rules, and intelligent meal alternatives.
"""

from typing import List, Dict, Any, Optional
import uuid
import copy
from collections import Counter
from itertools import product
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
    "en":"Follow fluid advice from your clinician; no individual fluid target is prescribed here.",
    "hi":"तरल की मात्रा के लिए डॉक्टर की सलाह मानें। यहाँ व्यक्तिगत मात्रा तय नहीं की जाती।",
    "mr":"द्रवपदार्थांच्या प्रमाणासाठी डॉक्टरांचा सल्ला पाळा. येथे वैयक्तिक प्रमाण ठरवत नाही."
}

def is_food_safe(
    food: Dict[str, Any],
    dietary_pref: str,
    allergies: List[str],
    restrictions: List[str],
    foods_avoided_freetext: Optional[str] = None
) -> bool:
    """Checks whether a food item matches user dietary preference, allergy constraints, and avoidance preferences."""
    if not food:
        return False
    # Check dietary preference
    food_diets = food.get("dietary_types", [])
    if dietary_pref == "vegan" and "vegan" not in food_diets:
        return False
    if dietary_pref == "vegetarian" and "vegetarian" not in food_diets and "vegan" not in food_diets:
        return False
    if dietary_pref == "eggetarian" and "eggetarian" not in food_diets and "vegetarian" not in food_diets and "vegan" not in food_diets:
        return False

    # Check allergies
    food_allergens = [a.lower().strip() for a in food.get("allergens", [])]
    for a in allergies:
        clean_a = a.strip().lower()
        if clean_a in ["none", ""]:
            continue
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
        if clean_r in ["none", ""]:
            continue
        if clean_r in ["no_peanuts"] and "peanuts" in food_allergens:
            return False
        if clean_r in ["no_dairy"] and "dairy" in food_allergens:
            return False
        if clean_r in ["no_gluten"] and "gluten" in food_allergens:
            return False
        if clean_r in ["no_beef_pork", "no_beef", "no_pork"]:
            # All dishes in default DB are pork and beef free, but safety check tags
            if any(tag in ["beef", "pork"] for tag in food.get("tags", [])):
                return False
        if clean_r == "low_spice" and not any(tag in food.get("tags",[]) for tag in ["low_spice","mild"]): return False
        if clean_r == "no_onion_garlic" and not any(tag in food.get("tags", []) for tag in ["jain", "no_onion_garlic"]):
            return False

    # Check free-text avoided foods
    if foods_avoided_freetext:
        disallowed_keywords = [w.strip().lower() for w in foods_avoided_freetext.split(",") if w.strip()]
        for kw in disallowed_keywords:
            if kw and (kw in food.get("name_en", "").lower() or kw in food.get("desc_en", "").lower() or kw in food_allergens):
                return False

    return True

def build_meal_item(
    food: Dict[str, Any],
    lang: str,
    dietary_pref: str,
    allergies: List[str],
    restrictions: List[str],
    foods_avoided_freetext: Optional[str] = None
) -> MealItem:
    """Builds a localized MealItem with safe alternatives."""
    name_field = f"name_{lang}" if f"name_{lang}" in food else "name_en"
    desc_field = f"desc_{lang}" if f"desc_{lang}" in food else "desc_en"
    portion_field = f"portion_{lang}" if f"portion_{lang}" in food else "portion_en"
    why_field = f"why_{lang}" if f"why_{lang}" in food else "why_en"

    # Assemble alternatives
    alternatives = []
    for alt_id in food.get("alternatives", []):
        alt_food = get_food_by_id(alt_id)
        if alt_food and is_food_safe(alt_food, dietary_pref, allergies, restrictions, foods_avoided_freetext):
            alt_name = alt_food.get(f"name_{lang}") or alt_food.get("name_en")
            alt_desc = alt_food.get(f"desc_{lang}") or alt_food.get("desc_en")
            alt_why = alt_food.get(f"why_{lang}") or alt_food.get("why_en")
            alternatives.append(MealAlternative(
                id=alt_food["id"],
                name=alt_name,
                description=alt_desc,
                prep_time_minutes=None,
                why_it_fits=alt_why,
                tags=alt_food.get("tags", [])
            ))

    # If alternatives count is < 2, pick additional safe candidates from database
    if len(alternatives) < 2:
        pool = [f for f in FOOD_DATABASE if f["meal_type"] == food["meal_type"] and f["id"] != food["id"]]
        for candidate in pool:
            if candidate["id"] not in [a.id for a in alternatives] and is_food_safe(candidate, dietary_pref, allergies, restrictions, foods_avoided_freetext):
                alt_name = candidate.get(f"name_{lang}") or candidate.get("name_en")
                alt_desc = candidate.get(f"desc_{lang}") or candidate.get("desc_en")
                alt_why = candidate.get(f"why_{lang}") or candidate.get("why_en")
                alternatives.append(MealAlternative(
                    id=candidate["id"],
                    name=alt_name,
                    description=alt_desc,
                    prep_time_minutes=None,
                    why_it_fits=alt_why,
                    tags=candidate.get("tags", [])
                ))
                if len(alternatives) >= 2:
                    break

    return MealItem(
        id=food["id"],
        meal_type=food["meal_type"],
        name=food.get(name_field, food["name_en"]),
        description=food.get(desc_field, food["desc_en"]),
        portion_guidance=food.get(portion_field, food.get("portion_en", "Standard portion")),
        why_recommended=food.get(why_field, food.get("why_en", "Provides balanced everyday nutrition.")),
        practical_prep_tips=food.get("prep_tips_en") if lang=="en" else ("सामग्री और मसाले अपने एलर्जी व आहार प्रतिबंधों के अनुसार चुनें।" if lang=="hi" else "साहित्य आणि मसाले तुमच्या ॲलर्जी व आहार निर्बंधांनुसार निवडा."),
        cultural_context={"en":"Familiar regional staple","hi":"परिचित क्षेत्रीय भोजन","mr":"परिचित प्रादेशिक पदार्थ"}[lang],
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
    supported_allergies = {"none", "", "peanut", "peanuts", "groundnut", "dairy", "milk", "lactose", "gluten", "wheat", "egg", "eggs", "fish", "seafood", "tree_nuts"}
    if any(item.strip().lower() not in supported_allergies for item in allergies):
        raise ValueError("This allergy is not covered by the food catalogue. Ask a clinician or dietitian; no exclusion was ignored.")

    restrictions = prefs.food_restrictions
    if any(item not in {"none","no_beef_pork","no_beef","no_pork","no_onion_garlic","low_spice","no_peanuts","no_dairy","no_gluten"} for item in restrictions):
        raise ValueError("This food restriction requires a clinician or dietitian; the catalogue cannot verify it.")
    avoided_text = prefs.foods_avoided_freetext
    known_conditions = prefs.known_conditions

    # Filter candidate food pools by safety
    safe_breakfasts = [f for f in FOOD_DATABASE if f["meal_type"] == "breakfast" and is_food_safe(f, dietary_pref, allergies, restrictions, avoided_text)]
    safe_lunches = [f for f in FOOD_DATABASE if f["meal_type"] == "lunch" and is_food_safe(f, dietary_pref, allergies, restrictions, avoided_text)]
    safe_dinners = [f for f in FOOD_DATABASE if f["meal_type"] == "dinner" and is_food_safe(f, dietary_pref, allergies, restrictions, avoided_text)]
    safe_snacks = [f for f in FOOD_DATABASE if f["meal_type"] == "snack" and is_food_safe(f, dietary_pref, allergies, restrictions, avoided_text)]

    pools = {"breakfast":safe_breakfasts,"lunch":safe_lunches,"dinner":safe_dinners,"snack":safe_snacks}
    if any(not pool for kind,pool in pools.items() if kind != "snack"):
        raise ValueError("No meals meet all restrictions. A dietitian can help; restrictions were not relaxed.")
    if prefs.meals_per_day == "2_meals":
        raise ValueError("A two-meal schedule needs individualized review; this planner currently supports three meals.")
    abnormal_canonicals = {b.get("canonical_name") for b in extractions if not b.get("requires_verification") and ((b.get("status")=="high" and b.get("canonical_name") in ["glucose_fasting","hba1c","cholesterol_total","cholesterol_ldl","triglycerides"]) or (b.get("status")=="low" and b.get("canonical_name") in ["hemoglobin","vitamin_d"]))}
    renal = any(b.get("canonical_name")=="creatinine_serum" and b.get("status") in ["high","low"] for b in extractions)
    complex_context = renal or prefs.age_group == "child" or any(condition in known_conditions for condition in ['ckd_renal','pregnancy','eating_disorder','serious_illness'])
    if complex_context:
        raise ValueError("Please review a personalized food plan with a clinician or dietitian for kidney concerns, children, pregnancy, or complex illness. No protein, mineral, or fluid prescription was generated.")

    def preference_score(food):
        alignments=set(food.get("lab_alignments",[])); tags=set(food.get("tags",[]))
        score=8*len(alignments & abnormal_canonicals)
        if "hemoglobin" in abnormal_canonicals: score+=6*bool(tags & {"iron_rich","heme_iron","folate"})
        if prefs.budget=="modest":
            score += 4 if any(word in food['name_en'].lower() for word in ['dal','gram','poha','chana','khichdi','roti']) else 0
            score -= 10 if any(word in food['name_en'].lower() for word in ['salmon','almond','walnut','quinoa']) else 0
        if prefs.cooking_availability=="quick_prep": score+=5*("quick_prep" in tags)
        if prefs.cooking_availability=="eating_out_often": score+=5*("balanced_plate" in tags)+3*any(word in food["name_en"].lower() for word in ["dal","rice","roti","idli"])
        if prefs.preferred_cuisine in ['maharashtrian','indian_regional']: score+=3*any(word in food['name_en'].lower() for word in ['poha','jowar','bajra','bhakri','besan','moong'])
        cuisine_words={"north_indian":["roti","paneer","dal","chana"],"south_indian":["idli","dosa","sambar","rasam"],"global_balanced":["salad","soup","bowl","oats"]}
        score+=5*any(word in food["name_en"].lower() for word in cuisine_words.get(prefs.preferred_cuisine,[]))
        if prefs.primary_goal=='support_energy': score+=int('high_protein' in tags)
        return score

    uses=Counter(); previous={}; used_days=set()
    combinations=list(product(safe_breakfasts,safe_lunches,safe_dinners))
    if len(combinations)<7:
        raise ValueError("Too few safe meal combinations for seven distinct days. Ask a dietitian; no restrictions were relaxed.")
    def choose_day():
        available=[items for items in combinations if tuple(food['id'] for food in items) not in used_days]
        items=max(available,key=lambda items:(sum(preference_score(food)-5*uses[food['id']]-20*(previous.get(food['meal_type'])==food['id']) for food in items),tuple(food['id'] for food in items)))
        used_days.add(tuple(food['id'] for food in items))
        for food in items: uses[food['id']]+=1;previous[food['meal_type']]=food['id']
        return items
    def choose_snack():
        food=max(safe_snacks,key=lambda food:preference_score(food)-5*uses[food['id']])
        uses[food['id']]+=1
        return food

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

    if "hemoglobin" in abnormal_canonicals:
        if lang == "hi":
            rationale_points.append("हीमोग्लोबिन स्तर को पोषण देने के लिए पालक, मेथी, भुने चने और नींबू (विटामिन सी) का समन्वय किया गया है।")
        elif lang == "mr":
            rationale_points.append("हिमोग्लोबिन वाढीस मदत करण्यासाठी पालक, मेथी, भाजलेले चणे आणि लिंबू यांचा योग्य मेळ घातला आहे.")
        else:
            rationale_points.append("Includes iron-supportive greens, legumes, and vitamin C pairings to enhance dietary iron utilization.")

    if not rationale_points:
        if lang == "hi":
            rationale_points.append("उपलब्ध पुष्ट नतीजों से कोई समर्थित विशेष आहार प्राथमिकता नहीं मिली। यह सामान्य शैक्षिक भोजन मार्गदर्शन है।")
        elif lang == "mr":
            rationale_points.append("उपलब्ध पुष्ट निकालांतून समर्थित विशेष आहार प्राधान्य मिळाले नाही. हे सामान्य शैक्षणिक आहार मार्गदर्शन आहे.")
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
    if "creatinine_serum" in abnormal_canonicals or "ckd_renal" in known_conditions:
        referral_recommended = True
        referral_reason = "Serum creatinine was flagged outside standard range or kidney condition was indicated. Strict clinical renal nutrition planning requires direct oversight by a qualified dietitian."
    elif "pregnancy" in known_conditions:
        referral_recommended = True
        referral_reason = "Pregnancy / lactation has unique maternal and fetal micronutrient requirements. Personalized consultation with your obstetrician or clinical nutritionist is recommended."
    elif "type2_diabetes" in known_conditions and ("glucose_fasting" in abnormal_canonicals or "hba1c" in abnormal_canonicals):
        referral_recommended = True
        referral_reason = {"en":"Medication-managed glycemic balance requires carbohydrate consistency coordinated with your prescribing physician.","hi":"मधुमेह की दवा लेते समय आहार में बदलाव और भोजन की नियमितता डॉक्टर से तय करें।","mr":"मधुमेहाची औषधे घेताना आहारातील बदल आणि जेवणाची नियमितता डॉक्टरांसोबत ठरवा."}[lang]

    # Build 7 distinct days
    days = []
    for day_idx in range(7):
        theme_obj = DAY_THEMES[day_idx]
        theme_title = theme_obj.get(lang) or theme_obj["en"]

        # Varied selection using round-robin rotation across safe pools
        bf_food,lu_food,di_food = choose_day()
        sn_food = choose_snack() if safe_snacks and prefs.meals_per_day=="3_meals_snacks" else None

        days.append(DailyNutritionPlan(
            day_number=day_idx + 1,
            day_name=f"Day {day_idx + 1}" if lang == "en" else f"दिन {day_idx + 1}" if lang == "hi" else f"दिवस {day_idx + 1}",
            focus_theme=theme_title,
            breakfast=build_meal_item(bf_food, lang, dietary_pref, allergies, restrictions, avoided_text),
            lunch=build_meal_item(lu_food, lang, dietary_pref, allergies, restrictions, avoided_text),
            dinner=build_meal_item(di_food, lang, dietary_pref, allergies, restrictions, avoided_text),
            snack=build_meal_item(sn_food, lang, dietary_pref, allergies, restrictions, avoided_text) if sn_food else None,
            hydration_guidance={"en":"Follow any fluid advice given by your clinician; this planner does not set an individual fluid target.","hi":"तरल की मात्रा के लिए डॉक्टर की सलाह मानें। यह योजना व्यक्तिगत मात्रा तय नहीं करती।","mr":"द्रवपदार्थांच्या प्रमाणासाठी डॉक्टरांचा सल्ला पाळा. ही योजना वैयक्तिक प्रमाण ठरवत नाही."}.get(lang)
        ))

    plan_title = "Personalized 7-Day Educational Food Guide"
    if lang == "hi":
        plan_title = "व्यक्तिगत ७-दिवसीय शैक्षिक आहार योजना"
    elif lang == "mr":
        plan_title = "वैयक्तिक ७-दिवसीय शैक्षणिक आहार मार्गदर्शक"

    return SevenDayNutritionPlan(
        planning_inputs={**prefs.model_dump(),"_clinical_signals":[{key:item.get(key) for key in ["canonical_name","status","requires_verification"]} for item in extractions]},
        foods_avoided_freetext=prefs.foods_avoided_freetext,
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
        disclaimer={"en":"This educational food plan does not diagnose or treat disease. Review individual needs with your clinician or dietitian.","hi":"यह शैक्षिक आहार योजना बीमारी का निदान या उपचार नहीं करती। व्यक्तिगत ज़रूरतें डॉक्टर या आहार विशेषज्ञ से जाँचें।","mr":"ही शैक्षणिक आहार योजना आजाराचे निदान किंवा उपचार करत नाही. वैयक्तिक गरजा डॉक्टर किंवा आहारतज्ज्ञांशी तपासा."}[lang]
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
    plan_dict = copy.deepcopy(plan_dict)
    new_food = get_food_by_id(new_meal_id)
    if not new_food or new_food.get("meal_type") != meal_type or not 1 <= day_number <= 7:
        raise ValueError("Invalid meal substitution.")

    dietary_pref = plan_dict.get("dietary_preference", "vegetarian")
    allergies = plan_dict.get("allergies", [])
    restrictions = plan_dict.get("food_restrictions", [])
    avoided_text = plan_dict.get("foods_avoided_freetext")

    # Check that new food is safe
    if not is_food_safe(new_food, dietary_pref, allergies, restrictions, avoided_text):
        raise ValueError("The alternative does not meet the saved dietary restrictions.")

    # Locate day
    for day in plan_dict.get("days", []):
        if day.get("day_number") == day_number:
            if meal_type in day:
                updated_item = build_meal_item(new_food, lang, dietary_pref, allergies, restrictions, avoided_text)
                day[meal_type] = updated_item.model_dump()
                break

    for day in plan_dict.get("days", []):
        for kind in ("breakfast","lunch","dinner","snack"):
            meal=day.get(kind)
            if meal and not is_food_safe(get_food_by_id(meal["id"]),dietary_pref,allergies,restrictions,avoided_text):
                raise ValueError("The full plan failed dietary validation.")
    return plan_dict
