import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { HomeScreen } from '../src/components/journey/HomeScreen';
import { Navigation } from '../src/components/common/Navigation';
import { QuestionnaireScreen } from '../src/components/journey/QuestionnaireScreen';
import { SimplifiedReportScreen } from '../src/components/journey/SimplifiedReportScreen';
import { LOCAL_SYNTHETIC_BIOMARKERS, LOCAL_SYNTHETIC_QUESTIONS, generateLocalReport } from '../src/fixtures/sampleData';

describe('Warm Clarity Patient Experience UI Tests (English, Hindi, Marathi)', () => {
  it('renders HomeScreen with patient-centric labels and privacy assurance in English', () => {
    render(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} language="en" />);
    expect(screen.getByText(/Understand your lab reports without the confusion/i)).toBeInTheDocument();
    expect(screen.getByText(/Private & confidential/i)).toBeInTheDocument();
    expect(screen.getByText('Upload a report')).toBeInTheDocument();
    expect(screen.getByText('Take a photo')).toBeInTheDocument();
  });

  it('renders HomeScreen in Hindi and Marathi consistently', () => {
    const { rerender } = render(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} language="hi" />);
    expect(screen.getByText(/बिना किसी उलझन के अपनी लैब रिपोर्ट को समझें/i)).toBeInTheDocument();
    expect(screen.getByText('रिपोर्ट अपलोड करें')).toBeInTheDocument();

    rerender(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} language="mr" />);
    expect(screen.getByText(/कोणत्याही गोंधळाशिवाय तुमचे लॅब रिपोर्ट समजून घ्या/i)).toBeInTheDocument();
    expect(screen.getByText('अहवाल अपलोड करा')).toBeInTheDocument();
  });

  it('renders Navigation with Home, My Reports, Profile, and quick language switchers', () => {
    let currentLang = 'en';
    render(
      <Navigation
        activeTab="home"
        onSelectTab={() => {}}
        language={currentLang}
        onSelectLanguage={(l) => { currentLang = l; }}
      />
    );
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('EN')).toBeInTheDocument();
    expect(screen.getByText('हिं')).toBeInTheDocument();
    expect(screen.getByText('मरा')).toBeInTheDocument();
  });

  it('renders QuestionnaireScreen and allows answering or skipping in all languages', () => {
    let submittedPayload = null;
    render(
      <QuestionnaireScreen
        questions={LOCAL_SYNTHETIC_QUESTIONS}
        onSubmitAnswers={(payload) => { submittedPayload = payload; }}
        onBack={() => {}}
        onSkipAll={() => { submittedPayload = []; }}
        language="en"
      />
    );
    expect(screen.getByText(/Step 1 of 2: A few questions about you/i)).toBeInTheDocument();
    expect(screen.getByText(/Question 1 of/i)).toBeInTheDocument();

    // Selecting an option
    const option = screen.getByText(/Yes, strictly fasted/i);
    fireEvent.click(option);

    // Clicking next progresses
    const nextBtn = screen.getByRole('button', { name: /Next question/i });
    fireEvent.click(nextBtn);

    // Clicking Skip all questions triggers submission
    const skipAllBtn = screen.getByRole('button', { name: /Skip all questions/i });
    fireEvent.click(skipAllBtn);
    expect(submittedPayload).toEqual([]);
  });

  it('renders SimplifiedReportScreen with abnormal-first findings and matching translations in Hindi and Marathi', () => {
    const reportEn = generateLocalReport('rep_test_en', [], 'en');
    const { rerender } = render(<SimplifiedReportScreen report={reportEn} onRestart={() => {}} language="en" />);
    expect(screen.getByText("Here's what we found")).toBeInTheDocument();
    expect(screen.getByText(/Overall Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/What needs attention/i)).toBeInTheDocument();
    expect(screen.getByText(/Download Summary PDF/i)).toBeInTheDocument();

    const reportHi = generateLocalReport('rep_test_hi', [], 'hi');
    rerender(<SimplifiedReportScreen report={reportHi} onRestart={() => {}} language="hi" />);
    expect(screen.getByText("जाँच में क्या सामने आया")).toBeInTheDocument();
    expect(screen.getByText("समग्र सारांश")).toBeInTheDocument();
    expect(screen.getByText(/किन बातों पर ध्यान देने की आवश्यकता है/i)).toBeInTheDocument();
    expect(screen.getByText("सारांश PDF डाउनलोड करें")).toBeInTheDocument();

    const reportMr = generateLocalReport('rep_test_mr', [], 'mr');
    rerender(<SimplifiedReportScreen report={reportMr} onRestart={() => {}} language="mr" />);
    expect(screen.getByText("तपासणीत काय आढळले")).toBeInTheDocument();
    expect(screen.getByText("एकूण सारांश")).toBeInTheDocument();
    expect(screen.getByText(/कशावर लक्ष देणे आवश्यक आहे/i)).toBeInTheDocument();
    expect(screen.getByText("अहवाल PDF डाउनलोड करा")).toBeInTheDocument();
  });

  it('renders InlineNutritionModal with 7-day food plan and localized controls', async () => {
    const { InlineNutritionModal } = await import('../src/components/journey/InlineNutritionModal');
    const { rerender } = render(
      <InlineNutritionModal
        isOpen={true}
        onClose={() => {}}
        reportId="rep_unit_test"
        language="en"
      />
    );

    // Initial fallback plan renders
    expect(screen.getByText(/Personalized 7-Day Nutrition Plan/i)).toBeInTheDocument();
    expect(screen.getByText(/Day 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Breakfast/i)).toBeInTheDocument();
    expect(screen.getByText(/Lunch/i)).toBeInTheDocument();
    expect(screen.getByText(/Dinner/i)).toBeInTheDocument();
    expect(screen.getByText(/Download Weekly Meal Guide/i)).toBeInTheDocument();

    // Rerender in Hindi
    rerender(
      <InlineNutritionModal
        isOpen={true}
        onClose={() => {}}
        reportId="rep_unit_test"
        language="hi"
      />
    );
    expect(screen.getByText(/व्यक्तिगत ७-दिवसीय आहार योजना/i)).toBeInTheDocument();
    expect(screen.getByText(/दिन 1/i)).toBeInTheDocument();
    expect(screen.getByText(/साप्ताहिक आहार योजना \(PDF\) डाउनलोड करें/i)).toBeInTheDocument();

    // Rerender in Marathi
    rerender(
      <InlineNutritionModal
        isOpen={true}
        onClose={() => {}}
        reportId="rep_unit_test"
        language="mr"
      />
    );
    expect(screen.getByText(/वैयक्तिक ७-दिवसीय आहार योजना/i)).toBeInTheDocument();
    expect(screen.getByText(/दिवस 1/i)).toBeInTheDocument();
    expect(screen.getByText(/साप्ताहिक आहार योजना \(PDF\) डाउनलोड करा/i)).toBeInTheDocument();
  });

  it('renders prominent InlineNutritionSection with heading "Your food plan, made for you" and 7-day schedule', async () => {
    const { InlineNutritionSection } = await import('../src/components/journey/InlineNutritionSection');
    render(
      <InlineNutritionSection
        reportId="rep_unit_test"
        language="en"
        isExpanded={true}
        onToggleExpand={() => {}}
      />
    );
    expect(screen.getByText(/Your food plan, made for you/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Day 1/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Breakfast/i)).toBeInTheDocument();
    expect(screen.getByText(/Lunch/i)).toBeInTheDocument();
    expect(screen.getByText(/Dinner/i)).toBeInTheDocument();
    expect(screen.getByText(/Download Weekly Meal Guide/i)).toBeInTheDocument();
  });

  it('renders InlineDoctorModal with nearby doctor discovery, calling, and appointments in EN, HI, MR', async () => {
    const { InlineDoctorModal } = await import('../src/components/journey/InlineDoctorModal');
    const { rerender } = render(
      <InlineDoctorModal
        isOpen={true}
        onClose={() => {}}
        reportId="rep_unit_test"
        language="en"
      />
    );

    expect(screen.getByText(/Find Nearby Clinics & Doctors/i)).toBeInTheDocument();
    expect(screen.getByText(/Use my location/i)).toBeInTheDocument();
    expect(screen.getByText(/List View/i)).toBeInTheDocument();
    expect(screen.getByText(/Map View/i)).toBeInTheDocument();

    // Rerender in Hindi
    rerender(
      <InlineDoctorModal
        isOpen={true}
        onClose={() => {}}
        reportId="rep_unit_test"
        language="hi"
      />
    );
    expect(screen.getByText(/निकटतम क्लीनिक एवं विशेषज्ञ डॉक्टर/i)).toBeInTheDocument();
    expect(screen.getByText(/मेरा स्थान उपयोग करें/i)).toBeInTheDocument();

    // Rerender in Marathi
    rerender(
      <InlineDoctorModal
        isOpen={true}
        onClose={() => {}}
        reportId="rep_unit_test"
        language="mr"
      />
    );
    expect(screen.getByText(/जवळचे दवाखाने व तज्ज्ञ डॉक्टर/i)).toBeInTheDocument();
    expect(screen.getByText(/माझे सध्याचे ठिकाण वापरा/i)).toBeInTheDocument();
  });

  it('renders prominent InlineDoctorSection with "Find the right care near you" and interactive tabs in EN, HI, MR', async () => {
    const { InlineDoctorSection } = await import('../src/components/journey/InlineDoctorSection');
    const { rerender } = render(
      <InlineDoctorSection
        reportId="rep_unit_test"
        language="en"
        isExpanded={true}
        onToggleExpand={() => {}}
      />
    );

    expect(screen.getByText(/Find the right care near you/i)).toBeInTheDocument();
    expect(screen.getByText(/Use my location/i)).toBeInTheDocument();
    expect(screen.getByText(/List View/i)).toBeInTheDocument();
    expect(screen.getByText(/Map View/i)).toBeInTheDocument();
    expect(screen.getByText(/My Appointments/i)).toBeInTheDocument();

    // Rerender in Hindi
    rerender(
      <InlineDoctorSection
        reportId="rep_unit_test"
        language="hi"
        isExpanded={true}
        onToggleExpand={() => {}}
      />
    );
    expect(screen.getByText(/अपने निकटतम सही चिकित्सा देखभाल खोजें/i)).toBeInTheDocument();
    expect(screen.getByText(/मेरा स्थान उपयोग करें/i)).toBeInTheDocument();
    expect(screen.getByText(/मेरी अपॉइंटमेंट्स/i)).toBeInTheDocument();

    // Rerender in Marathi
    rerender(
      <InlineDoctorSection
        reportId="rep_unit_test"
        language="mr"
        isExpanded={true}
        onToggleExpand={() => {}}
      />
    );
    expect(screen.getByText(/तुमच्या जवळ योग्य वैद्यकीय मदत शोधा/i)).toBeInTheDocument();
    expect(screen.getByText(/माझे सध्याचे ठिकाण वापरा/i)).toBeInTheDocument();
    expect(screen.getByText(/माझ्या नियोजित भेटी/i)).toBeInTheDocument();
  });
});


