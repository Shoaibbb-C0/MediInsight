import React from 'react';
import { TRANSLATIONS } from '../../fixtures/translations';

export function Navigation({ activeTab, onSelectTab, language = 'en', onSelectLanguage }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  const tabs = [
    { id: 'home', label: t.home, icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    )},
    { id: 'reports', label: t.reports, icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    )},
    { id: 'profile', label: t.profile, icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    )},
  ];

  return (
    <nav className="bg-clarity-surface/95 backdrop-blur border-b border-clarity-border sticky top-0 z-40" aria-label="Main Navigation">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2.5 cursor-pointer" onClick={() => onSelectTab('home')}>
            <div className="w-8 h-8 rounded-xl bg-clarity-teal flex items-center justify-center text-clarity-surface font-bold text-lg shadow-sm">
              S
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg tracking-tight text-clarity-teal leading-none">Simplifier</span>
              <span className="text-[11px] font-medium text-clarity-muted">{t.tagline}</span>
            </div>
          </div>

          <div className="flex items-center space-x-1 sm:space-x-3">
            {/* Quick Language Switcher */}
            <div className="flex items-center bg-clarity-ivory p-1 rounded-xl border border-clarity-border/80">
              <button
                type="button"
                onClick={() => onSelectLanguage && onSelectLanguage('en')}
                className={`px-2 py-1 text-xs font-semibold rounded-lg transition-all ${
                  language === 'en'
                    ? 'bg-clarity-teal text-white shadow-sm'
                    : 'text-clarity-muted hover:text-clarity-charcoal'
                }`}
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => onSelectLanguage && onSelectLanguage('hi')}
                className={`px-2 py-1 text-xs font-semibold rounded-lg font-devanagari transition-all ${
                  language === 'hi'
                    ? 'bg-clarity-teal text-white shadow-sm'
                    : 'text-clarity-muted hover:text-clarity-charcoal'
                }`}
              >
                हिं
              </button>
              <button
                type="button"
                onClick={() => onSelectLanguage && onSelectLanguage('mr')}
                className={`px-2 py-1 text-xs font-semibold rounded-lg font-devanagari transition-all ${
                  language === 'mr'
                    ? 'bg-clarity-teal text-white shadow-sm'
                    : 'text-clarity-muted hover:text-clarity-charcoal'
                }`}
              >
                मरा
              </button>
            </div>

            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onSelectTab(tab.id)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-clarity-teal text-clarity-surface shadow-sm'
                      : 'text-clarity-muted hover:text-clarity-charcoal hover:bg-clarity-ivory'
                  }`}
                >
                  {tab.icon}
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
