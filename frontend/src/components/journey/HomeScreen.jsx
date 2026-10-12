import React from 'react';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function HomeScreen({ onStartUpload, onStartCamera, onViewSample, language = 'en' }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 sm:py-14 text-center">
      {/* Privacy assurance pill */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-clarity-mint/40 text-clarity-teal text-xs font-semibold mb-6">
        <svg className="w-4 h-4 text-clarity-teal shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>{t.privateBadge}</span>
      </div>

      {/* Warm patient headline */}
      <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-clarity-teal leading-tight sm:leading-tight mb-4">
        {t.heroTitle}
      </h1>

      {/* Gentle supporting explanation */}
      <p className="text-base sm:text-lg text-clarity-muted leading-relaxed max-w-xl mx-auto mb-10">
        {t.heroSubtitle}
      </p>

      {/* Two clear primary upload choices */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto mb-12">
        <Button
          size="lg"
          variant="primary"
          onClick={onStartUpload}
          className="w-full sm:w-1/2 py-4 shadow-md text-base"
          icon={(
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          )}
        >
          {t.uploadButton}
        </Button>

        <Button
          size="lg"
          variant="secondary"
          onClick={onStartCamera}
          className="w-full sm:w-1/2 py-4 text-base"
          icon={(
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          )}
        >
          {t.cameraButton}
        </Button>
      </div>

      {/* Try sample fixture button */}
      <div className="pt-4 border-t border-clarity-border/60">
        <button
          onClick={onViewSample}
          className="inline-flex items-center gap-2 text-sm text-clarity-teal/80 hover:text-clarity-teal font-medium hover:underline cursor-pointer"
        >
          <span className="font-semibold text-clarity-teal underline">{t.trySample}</span>
        </button>
      </div>

      {/* Three clear reassurance pillars */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left mt-12 pt-8 border-t border-clarity-border/40">
        <div className="p-4 bg-clarity-surface rounded-2xl border border-clarity-border/60 shadow-soft">
          <div className="w-8 h-8 rounded-lg bg-clarity-mint/50 flex items-center justify-center text-clarity-teal font-bold mb-3">
            1
          </div>
          <h2 className="font-bold text-clarity-teal text-base mb-1">
            {language === 'hi' ? 'सिम्प्लीफायर क्या करता है' : language === 'mr' ? 'सिम्प्लीफायर काय करते' : 'What Simplifier does'}
          </h2>
          <p className="text-xs sm:text-sm text-clarity-muted leading-relaxed">
            {language === 'hi' ? 'जटिल संख्याओं और संदर्भ सीमाओं को सरल दैनिक भाषा में अनुवादित करता है।' : language === 'mr' ? 'क्लिष्ट आकडेवारी आणि संदर्भ मर्यादांचे सोप्या भाषेत स्पष्टीकरण देते.' : 'Translates numbers and clinical reference ranges into friendly everyday language.'}
          </p>
        </div>

        <div className="p-4 bg-clarity-surface rounded-2xl border border-clarity-border/60 shadow-soft">
          <div className="w-8 h-8 rounded-lg bg-clarity-mint/50 flex items-center justify-center text-clarity-teal font-bold mb-3">
            2
          </div>
          <h2 className="font-bold text-clarity-teal text-base mb-1">
            {language === 'hi' ? 'शुरुआत कैसे करें' : language === 'mr' ? 'सुरुवात कशी करावी' : 'How you start'}
          </h2>
          <p className="text-xs sm:text-sm text-clarity-muted leading-relaxed">
            {language === 'hi' ? 'अपने पेपर पर्चे का फोटो लें या PDF चुनें। हम इसे चरणबद्ध तरीके से समझाएंगे।' : language === 'mr' ? 'कागदी रिपोर्टचा फोटो काढा किंवा PDF निवडा. आम्ही टप्प्याटप्प्याने समजावून सांगू.' : 'Snap a picture of your paper lab slip or choose a PDF. We organize it step-by-step.'}
          </p>
        </div>

        <div className="p-4 bg-clarity-surface rounded-2xl border border-clarity-border/60 shadow-soft">
          <div className="w-8 h-8 rounded-lg bg-clarity-mint/50 flex items-center justify-center text-clarity-teal font-bold mb-3">
            3
          </div>
          <h2 className="font-bold text-clarity-teal text-base mb-1">
            {language === 'hi' ? 'निजी एवं सुरक्षित' : language === 'mr' ? 'खाजगी आणि सुरक्षित' : 'Private & Secure'}
          </h2>
          <p className="text-xs sm:text-sm text-clarity-muted leading-relaxed">
            {language === 'hi' ? 'आपकी जानकारी केवल स्थानीय सत्र में सुरक्षित रहती है और किसी तीसरे पक्ष को नहीं दी जाती।' : language === 'mr' ? 'तुमची माहिती स्थानिक पातळीवर सुरक्षित राहते आणि इतर कोणालाही दिली जात नाही.' : 'Your results are processed locally in private sessions and never sold to third parties.'}
          </p>
        </div>
      </div>
    </div>
  );
}
