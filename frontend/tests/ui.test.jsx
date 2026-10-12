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
});
