-- Simplifier 2.0 Feature 3: Appointments Schema and Strict Owner Row Level Security (RLS)
-- Supports atomic slot reservations, cancellation, and owner isolation

CREATE TABLE IF NOT EXISTS public.patient_appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id TEXT NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    doctor_id TEXT NOT NULL,
    doctor_name TEXT NOT NULL,
    clinic_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    slot TEXT NOT NULL,
    patient_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'confirmed',
    booking_capability TEXT NOT NULL DEFAULT 'direct_booking',
    phone TEXT,
    whatsapp_number TEXT,
    address TEXT NOT NULL,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    is_demo BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_doctor_slot_active UNIQUE (doctor_id, slot)
);

-- Index for speedy owner retrieval and doctor lookup
CREATE INDEX IF NOT EXISTS idx_appointments_user ON public.patient_appointments(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON public.patient_appointments(doctor_id);

-- Enable RLS
ALTER TABLE public.patient_appointments ENABLE ROW LEVEL SECURITY;

-- Policies: Patients can only view, create, update, or cancel their own appointments
CREATE POLICY "Patients view their own appointments only"
    ON public.patient_appointments FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Patients insert their own appointments only"
    ON public.patient_appointments FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Patients update their own appointments only"
    ON public.patient_appointments FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Patients delete their own appointments only"
    ON public.patient_appointments FOR DELETE
    USING (auth.uid() = user_id);
