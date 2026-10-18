import pytest
from app.schemas.nutrition import NutritionPreferencesSubmission
from app.services.nutrition_planner import generate_seven_day_plan,swap_meal_in_plan,is_food_safe
from app.services.nutrition_database import get_food_by_id


def plan(signals=None,**preferences):
    readings=[{'canonical_name':name,'status':status} for name,status in (signals or [])]
    return generate_seven_day_plan('personalization',readings,NutritionPreferencesSubmission(report_id='personalization',**preferences)).model_dump()

def selected(result):return [day[kind]['id'] for day in result['days'] for kind in ['breakfast','lunch','dinner']]

@pytest.mark.parametrize('signals,preferences',[
    ([('hemoglobin','low')],{'dietary_preference':'vegetarian'}),
    ([('hemoglobin','low')],{'dietary_preference':'non_vegetarian'}),
    ([('glucose_fasting','high')],{}),
    ([('cholesterol_total','high')],{}),
    ([('glucose_fasting','high'),('hemoglobin','low'),('cholesterol_total','high')],{}),
    ([],{}),([],{'allergies':['peanuts']}),([],{'allergies':['dairy']}),([],{'budget':'modest'}),([],{'age_group':'older_adult'}),
])
def test_nutrition_constraints_and_real_input_scoring(signals,preferences):
    result=plan(signals,**preferences)
    assert len(result['days'])==7
    assert len(set(tuple(day[kind]['id'] for kind in ['breakfast','lunch','dinner']) for day in result['days']))==7
    for day in result['days']:
        for kind in ['breakfast','lunch','dinner']:
            food=get_food_by_id(day[kind]['id'])
            assert is_food_safe(food,result['dietary_preference'],result['allergies'],result['food_restrictions'])
            for alternative in day[kind]['alternatives']:
                assert is_food_safe(get_food_by_id(alternative['id']),result['dietary_preference'],result['allergies'],result['food_restrictions'])
    assert result['planning_inputs']['age_group']==preferences.get('age_group','adult')

def test_report_and_dietary_inputs_change_selected_meals():
    normal=selected(plan())
    assert selected(plan([('hemoglobin','low')]))!=normal
    assert selected(plan([('glucose_fasting','high')]))!=normal
    assert selected(plan([('cholesterol_total','high')]))!=normal
    assert selected(plan([('hemoglobin','low')],dietary_preference='non_vegetarian'))!=selected(plan([('hemoglobin','low')],dietary_preference='vegetarian'))
    assert selected(plan(budget='modest'))!=normal

def test_impossible_allergies_never_relaxed():
    with pytest.raises(ValueError,match='restrictions'):
        plan(allergies=['gluten','dairy','peanuts','eggs','fish'],foods_avoided_freetext='rice,dal,gram,roti,poha,oats,vegetable,fruit,moong,paneer,khichdi,besan,idli,upma,chicken')

@pytest.mark.parametrize('context',[{'age_group':'child'},{'known_conditions':['ckd_renal']},{'known_conditions':['pregnancy']}])
def test_complex_context_is_referred_not_prescribed(context):
    with pytest.raises(ValueError,match='clinician or dietitian'):plan(**context)

def test_unsafe_and_wrong_meal_swaps_are_rejected_without_mutation():
    original=plan(allergies=['dairy'])
    snapshot=selected(original)
    with pytest.raises(ValueError):swap_meal_in_plan(original,1,'breakfast','di_palak_paneer')
    assert selected(original)==snapshot
    with pytest.raises(ValueError):swap_meal_in_plan(original,1,'breakfast','not-a-food')


def test_unrecognized_allergy_is_not_silently_ignored():
    with pytest.raises(ValueError, match="not covered"):
        plan(allergies=["mustard"])


def test_onion_garlic_restriction_requires_explicit_catalogue_evidence():
    assert not is_food_safe({"dietary_types":["vegan"],"desc_en":"A vegetable dish", "tags":[]}, "vegan", [], ["no_onion_garlic"])
