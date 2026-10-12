-- Simplifier 2.0 Feature 2: Personalized Nutrition Schema & RLS Policies
-- Enables strict patient ownership and secure storage for personalized food plans

CREATE TABLE IF NOT EXISTS public.patient_nutrition_plans (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    report_id TEXT NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
    language TEXT NOT NULL DEFAULT 'en',
    version TEXT NOT NULL DEFAULT '2.0.0',
    plan_title TEXT NOT NULL,
    clinical_basis_summary TEXT,
    dietary_preference TEXT NOT NULL DEFAULT 'vegetarian',
    allergies TEXT[] DEFAULT '{}',
    food_restrictions TEXT[] DEFAULT '{}',
    plan_data JSONB NOT NULL,
    dietitian_referral_recommended BOOLEAN DEFAULT FALSE,
    dietitian_referral_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.patient_nutrition_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Patients can view their own nutrition plans only"
    ON public.patient_nutrition_plans FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Patients can insert their own nutrition plans only"
    ON public.patient_nutrition_plans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Patients can update their own nutrition plans only"
    ON public.patient_nutrition_plans FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Patients can delete their own nutrition plans only"
    ON public.patient_nutrition_plans FOR DELETE
    USING (auth.uid() = user_id);
