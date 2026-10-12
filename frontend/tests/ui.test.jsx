import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { HomeScreen } from '../src/components/journey/HomeScreen';
import { Navigation } from '../src/components/common/Navigation';
import { VerificationScreen } from '../src/components/verification/VerificationScreen';
import { QuestionnaireScreen } from '../src/components/journey/QuestionnaireScreen';
import { SimplifiedReportScreen } from '../src/components/journey/SimplifiedReportScreen';
import { LOCAL_SYNTHETIC_BIOMARKERS, LOCAL_SYNTHETIC_QUESTIONS, generateLocalReport } from '../src/fixtures/sampleData';

describe('Warm Clarity Patient Experience UI Tests', () => {
  it('renders HomeScreen with patient-centric labels and privacy assurance', () => {
    render(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} />);
    expect(screen.getByText(/Understand your lab reports without the confusion/i)).toBeInTheDocument();
    expect(screen.getByText(/Private & confidential/i)).toBeInTheDocument();
    expect(screen.getByText('Upload a report')).toBeInTheDocument();
    expect(screen.getByText('Take a photo')).toBeInTheDocument();
  });

  it('renders Navigation with Home, My Reports, and Profile tabs without dead ends', () => {
    let selected = 'home';
    render(<Navigation activeTab={selected} onSelectTab={(t) => { selected = t; }} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('My Reports')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('renders VerificationScreen with source inspection, row highlights, and editable correction', () => {
    render(<VerificationScreen biomarkers={LOCAL_SYNTHETIC_BIOMARKERS} onConfirmAll={() => {}} onBack={() => {}} />);
    expect(screen.getByText("Let's check a few details")).toBeInTheDocument();
    expect(screen.getByText(/Document Preview/i)).toBeInTheDocument();
    
    // Check editable input exists
    const input = screen.getByLabelText(/Corrected value if printed differently/i);
    expect(input).toBeInTheDocument();
    fireEvent.change(input, { target: { value: '6.4' } });
    expect(input.value).toBe('6.4');

    // Click Save Correction
    const saveBtn = screen.getByRole('button', { name: /Save Correction/i });
    fireEvent.click(saveBtn);
    expect(screen.getByText(/Recorded! Value updated for your report analysis./i)).toBeInTheDocument();
  });

  it('renders QuestionnaireScreen and allows answering or skipping', () => {
    let submittedPayload = null;
    render(
      <QuestionnaireScreen
        questions={LOCAL_SYNTHETIC_QUESTIONS}
        onSubmitAnswers={(payload) => { submittedPayload = payload; }}
        onBack={() => {}}
        onSkipAll={() => { submittedPayload = []; }}
      />
    );
    expect(screen.getByText('A few questions about you')).toBeInTheDocument();
    expect(screen.getByText(/Question 1 of/i)).toBeInTheDocument();

    // Selecting an option
    const option = screen.getByText(/Yes, I fasted for 10\+ hours/i);
    fireEvent.click(option);

    // Clicking next progresses
    const nextBtn = screen.getByRole('button', { name: /Next question/i });
    fireEvent.click(nextBtn);

    // Clicking Skip all questions triggers submission
    const skipAllBtn = screen.getByRole('button', { name: /Skip all questions/i });
    fireEvent.click(skipAllBtn);
    expect(submittedPayload).toEqual([]);
  });

  it('renders SimplifiedReportScreen with plain English explanation and disclaimer', () => {
    const report = generateLocalReport('rep_test', []);
    render(<SimplifiedReportScreen report={report} onRestart={() => {}} />);
    expect(screen.getByText("Here's what we found")).toBeInTheDocument();
    expect(screen.getByText(/Overall Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/Important Medical Notice/i)).toBeInTheDocument();
    expect(screen.getByText(/Phase 3 Clinical Interpretation/i)).toBeInTheDocument();
  });
});
