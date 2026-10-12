-- Simplifier 2.0 Production PostgreSQL Schema & Row Level Security (RLS)
-- Enables strict patient owner isolation and secure storage policies

-- 1. Patient Profiles Table
CREATE TABLE IF NOT EXISTS public.patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    preferred_language TEXT NOT NULL DEFAULT 'en',
    age_bracket TEXT,
    sex_assigned_at_birth TEXT,
    is_pregnant BOOLEAN,
    known_conditions TEXT[] DEFAULT '{}',
    current_medications TEXT[] DEFAULT '{}',
    allergies TEXT[] DEFAULT '{}',
    reported_symptoms TEXT[] DEFAULT '{}',
    testing_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_user_profile UNIQUE (user_id)
);

-- Enable RLS
ALTER TABLE public.patient_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Patients can view their own profile only"
    ON public.patient_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Patients can update their own profile only"
    ON public.patient_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Patients can insert their own profile only"
    ON public.patient_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Patients can delete their own profile only"
    ON public.patient_profiles FOR DELETE
    USING (auth.uid() = user_id);

-- 2. Laboratory Reports Table
CREATE TABLE IF NOT EXISTS public.reports (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Patients can view their own reports only"
    ON public.reports FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Patients can insert their own reports only"
    ON public.reports FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Patients can delete their own reports only"
    ON public.reports FOR DELETE
    USING (auth.uid() = user_id);

-- 3. Extracted Biomarkers Table
CREATE TABLE IF NOT EXISTS public.report_extractions (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    value TEXT NOT NULL,
    unit TEXT NOT NULL,
    reference_range TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence NUMERIC(4, 3) NOT NULL,
    requires_verification BOOLEAN NOT NULL DEFAULT FALSE,
    original_extracted_value TEXT,
    corrected_value TEXT,
    correction_provenance TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.report_extractions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Patients can view their own biomarker extractions"
    ON public.report_extractions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Patients can update their own biomarker corrections"
    ON public.report_extractions FOR UPDATE
    USING (auth.uid() = user_id);

-- 4. Doctor Appointments Table
CREATE TABLE IF NOT EXISTS public.doctor_appointments (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    doctor_id TEXT NOT NULL,
    doctor_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    slot TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'CONFIRMED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.doctor_appointments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Patients can manage their own appointments"
    ON public.doctor_appointments FOR ALL
    USING (auth.uid() = user_id);
