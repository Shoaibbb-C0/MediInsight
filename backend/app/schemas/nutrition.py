"""
Pydantic Schemas for Feature 2: Production-Grade Personalized Nutrition System.
Includes Dietary Preferences, Smart Questionnaire, Meal Items, 7-Day Plan,
Alternatives/Swapping, and Safety Notes.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import datetime

class NutritionQuestionOption(BaseModel):
    id: str
    text: str
    description: Optional[str] = None

class NutritionQuestion(BaseModel):
    id: str
    category: str  # 'dietary_pref', 'allergies', 'restrictions', 'routine', 'budget', 'goals'
    text: str
    context_reason: str
    is_multi_select: bool = False
    options: List[NutritionQuestionOption]

class NutritionPreferencesSubmission(BaseModel):
    age_group: Literal["adult", "older_adult", "child"] = "adult"
    user_id: str = "local_default_patient"
    report_id: str
    dietary_preference: Literal["vegetarian", "non_vegetarian", "vegan", "eggetarian"] = "vegetarian"  # 'vegetarian', 'non_vegetarian', 'vegan', 'eggetarian'
    allergies: List[str] = Field(default_factory=list, max_length=30)  # e.g., 'peanuts', 'gluten', 'dairy', 'shellfish'
    food_restrictions: List[str] = Field(default_factory=list)  # e.g., 'no_beef', 'no_pork', 'low_spice', 'no_onion_garlic'
    meals_per_day: Literal["2_meals", "3_meals", "3_meals_snacks"] = "3_meals"  # '2_meals', '3_meals', '3_meals_snacks'
    budget: Literal["modest", "moderate", "flexible"] = "moderate"  # 'modest', 'moderate', 'flexible'
    preferred_cuisine: str = "indian_regional"  # 'indian_regional', 'north_indian', 'south_indian', 'global_balanced'
    foods_avoided_freetext: Optional[str] = Field(default=None, max_length=500)
    known_conditions: List[str] = Field(default_factory=list)  # e.g., 'ckd_renal', 'type2_diabetes', 'pregnancy'
    primary_goal: str = "understand_lab_choices"  # 'balanced_wellness', 'understand_lab_choices', 'support_energy'
    cooking_availability: str = "home_cooked"  # 'quick_prep', 'home_cooked', 'eating_out_often'
    answers_map: Dict[str, Any] = Field(default_factory=dict)

class MealAlternative(BaseModel):
    id: str
    name: str
    description: str
    prep_time_minutes: Optional[int] = 20
    why_it_fits: str
    tags: List[str] = Field(default_factory=list)

class MealItem(BaseModel):
    id: str
    meal_type: str  # 'breakfast', 'lunch', 'dinner', 'snack'
    name: str
    description: str
    portion_guidance: str
    why_recommended: str
    practical_prep_tips: Optional[str] = None
    cultural_context: Optional[str] = None
    alternatives: List[MealAlternative] = Field(default_factory=list)
    selected_alternative_id: Optional[str] = None

class DailyNutritionPlan(BaseModel):
    day_number: int  # 1 to 7
    day_name: str  # 'Monday', 'Day 1', etc.
    focus_theme: str
    breakfast: MealItem
    lunch: MealItem
    dinner: MealItem
    snack: Optional[MealItem] = None
    hydration_guidance: str

class SevenDayNutritionPlan(BaseModel):
    planning_inputs: Dict[str, Any] = Field(default_factory=dict)
    planner_version: str = "constraint-score-v1"
    foods_avoided_freetext: Optional[str] = Field(default=None, max_length=500)
    plan_id: str
    report_id: str
    user_id: str
    language: str = "en"
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    version: str = "2.0.0"
    plan_title: str
    clinical_basis_summary: str
    dietary_preference: str
    allergies: List[str]
    food_restrictions: List[str]
    days: List[DailyNutritionPlan]
    safety_guidance: List[str]
    dietitian_referral_recommended: bool = False
    dietitian_referral_reason: Optional[str] = None
    disclaimer: str

class SwapMealRequest(BaseModel):
    plan_id: str
    day_number: int
    meal_type: str  # 'breakfast', 'lunch', 'dinner', 'snack'
    new_meal_id: str  # Alternative ID or new meal name
