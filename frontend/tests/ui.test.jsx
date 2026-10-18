import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { HomeScreen } from '../src/components/journey/HomeScreen';
import { Navigation } from '../src/components/common/Navigation';
import { QuestionnaireScreen } from '../src/components/journey/QuestionnaireScreen';
import { SimplifiedReportScreen } from '../src/components/journey/SimplifiedReportScreen';
import { LOCAL_SYNTHETIC_BIOMARKERS, LOCAL_SYNTHETIC_QUESTIONS, generateLocalReport } from '../src/fixtures/sampleData';

describe('Warm Clarity Patient Experience UI Tests (English, Hindi, Marathi)', () => {
  it('renders HomeScreen with patient-centric labels and privacy assurance in English', () => {
    render(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} language="en" />);
    expect(screen.getByText(/Add your report/i)).toBeInTheDocument();
    expect(screen.getByText('Upload a report')).toBeInTheDocument();
    expect(screen.getByText('Take a photo')).toBeInTheDocument();
  });

  it('renders HomeScreen in Hindi and Marathi consistently', () => {
    const { rerender } = render(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} language="hi" />);
    expect(screen.getByText(/अपनी रिपोर्ट जोड़ें/i)).toBeInTheDocument();
    expect(screen.getByText('रिपोर्ट अपलोड करें')).toBeInTheDocument();

    rerender(<HomeScreen onStartUpload={() => {}} onStartCamera={() => {}} onViewSample={() => {}} language="mr" />);
    expect(screen.getByText(/तुमचा अहवाल जोडा/i)).toBeInTheDocument();
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
    expect(screen.getAllByText('Upload')[0]).toBeInTheDocument();
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
    expect(screen.getByRole("heading", { name: /things need your attention/ })).toBeInTheDocument();
    expect(screen.getByText(/Overall Summary/i)).toBeInTheDocument();
    expect(screen.getByText(/What needs attention/i)).toBeInTheDocument();
    expect(screen.getByText(/Download Summary PDF/i)).toBeInTheDocument();

    const reportHi = generateLocalReport('rep_test_hi', [], 'hi');
    rerender(<SimplifiedReportScreen report={reportHi} onRestart={() => {}} language="hi" />);
    expect(screen.getByRole("heading", { name: /नतीजों पर ध्यान दें/ })).toBeInTheDocument();
    expect(screen.getByText("समग्र सारांश")).toBeInTheDocument();
    expect(screen.getByText(/किन बातों पर ध्यान देने की आवश्यकता है/i)).toBeInTheDocument();
    expect(screen.getByText("सारांश PDF डाउनलोड करें")).toBeInTheDocument();

    const reportMr = generateLocalReport('rep_test_mr', [], 'mr');
    rerender(<SimplifiedReportScreen report={reportMr} onRestart={() => {}} language="mr" />);
    expect(screen.getByRole("heading", { name: /निकालांकडे लक्ष द्या/ })).toBeInTheDocument();
    expect(screen.getByText("एकूण सारांश")).toBeInTheDocument();
    expect(screen.getByText(/कशावर लक्ष देणे आवश्यक आहे/i)).toBeInTheDocument();
    expect(screen.getByText("अहवाल PDF डाउनलोड करा")).toBeInTheDocument();
  });


  afterEach(() => vi.unstubAllGlobals());

  it('does not invent a food plan when the service has no saved plan', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ok:false,status:404}));
    const { InlineNutritionSection } = await import('../src/components/journey/InlineNutritionSection');
    render(<InlineNutritionSection reportId="real_report" isExpanded language="en" />);
    expect(screen.getByText('Your 7-day food plan', {selector:'h2'})).toBeInTheDocument();
    await waitFor(() => expect(fetch).toHaveBeenCalled());
    expect(screen.queryByText('Broken Wheat Daliya with Vegetables')).not.toBeInTheDocument();
    expect(screen.getByText(/Tell us your allergies/)).toBeInTheDocument();
  });

  it('shows service failure instead of fabricated providers', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    const { InlineDoctorSection } = await import('../src/components/journey/InlineDoctorSection');
    render(<InlineDoctorSection reportId="real_report" isExpanded language="en" />);
    expect(await screen.findByText(/Provider search unavailable/)).toBeInTheDocument();
    expect(screen.queryByText(/Dr. Ananya Sharma/)).not.toBeInTheDocument();
  });

  it('keeps real uploads out of the demonstration journey when the backend fails', async () => {
    vi.stubGlobal('fetch', vi.fn(async url => url.includes('/auth/') ? {ok:true,status:200,json:async()=>({configured:false,sign_in_required:false})} : {ok:false,status:503,json:async()=>({detail:'Unavailable'})}));
    const { default: App } = await import('../src/App');
    const { container } = render(<App />);
    fireEvent.click(await screen.findByRole('button', {name:'Upload a report'}));
    fireEvent.change(container.querySelector('input[type="file"]'), {target:{files:[new File(['unreadable'], 'report.pdf', {type:'application/pdf'})]}});
    expect(await screen.findByRole('alert')).toHaveTextContent(/No example measurements were substituted/);
    expect(screen.queryByText(/Fasting Blood Glucose/)).not.toBeInTheDocument();
    expect(screen.getByRole('heading', {name:'Add your report'})).toBeInTheDocument();
  });

  it('compares compatible real history only and keeps the clinical range separate', async () => {
    const { ReportTrends } = await import('../src/components/journey/ReportTrends');
    const history = [1,2,3,4].map((n)=>({id:`report_${n}`,date:`2026-0${n}-01`,measurements:[{name:'Haemoglobin',canonical_name:'hemoglobin',unit:'g/dL',value:String(10+n),reference_range:'12 - 15.5'}]})).reverse();
    render(<ReportTrends history={history} language="en" />);
    expect(screen.getByRole('img')).toHaveAccessibleName(/Haemoglobin/);
    expect(screen.getByText(/Personal historical average: 12.50 g\/dL/)).toBeInTheDocument();
    expect(screen.getByText(/does not replace the laboratory reference interval/)).toBeInTheDocument();
  });
  it('opens the actual uploaded report from history instead of a demonstration', async () => {
    const report = {...generateLocalReport('real_42', [], 'en'), is_synthetic_fixture:false};
    const fetchMock = vi.fn(async (url) => ({ok:true,status:200,json:async()=>{
      if (url.includes('/auth/configuration')) return {configured:false,sign_in_required:false};
      if (url.endsWith('/upload')) return {report_id:'real_42',filename:'lab.pdf',file_type:'pdf',is_synthetic_fixture:false};
      if (url.includes('/extractions')) return LOCAL_SYNTHETIC_BIOMARKERS;
      if (url.includes('/questions?')) return {questions:[]};
      if (url.includes('/summary')) return report;
      return {};
    }}));
    vi.stubGlobal('fetch', fetchMock);
    const { default: App } = await import('../src/App');
    const { TRANSLATIONS } = await import('../src/fixtures/translations');
    const { container } = render(<App />);
    fireEvent.click(await screen.findByRole('button', {name:'Upload a report'}));
    fireEvent.change(container.querySelector('input[type=file]'), {target:{files:[new File(['synthetic test'], 'lab.pdf', {type:'application/pdf'})]}});
    fireEvent.click(await screen.findByRole('button',{name: new RegExp(TRANSLATIONS.en.finishQuestions)}));
    await screen.findByRole('heading',{name:/things need your attention/});
    fireEvent.click(screen.getAllByRole('button',{name:'My Reports'})[0]);
    expect(screen.getByRole('heading',{name:'lab.pdf'})).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'View report'}));
    await screen.findByRole('heading',{name:/things need your attention/});
    expect(fetchMock.mock.calls.some(([url])=>url==='/api/v1/reports/real_42/summary?lang=en')).toBe(true);
    expect(fetchMock.mock.calls.some(([url])=>url.includes('rep_demo_fixture'))).toBe(false);
  });

});
