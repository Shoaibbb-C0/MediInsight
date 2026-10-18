import React from 'react';
import { FileUp, Files, UserRound, Utensils, Stethoscope, Activity } from 'lucide-react';
import { TRANSLATIONS } from '../../fixtures/translations';

export function Navigation({ activeTab, onSelectTab, language = 'en', onSelectLanguage }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const tabs = [
    {id:'home', label: language==='hi'?'अपलोड':language==='mr'?'अपलोड':'Upload', Icon:FileUp},
    {id:'reports', label:t.reports, Icon:Files},
    {id:'nutrition', label:language==='hi'?'आहार':language==='mr'?'आहार':'Nutrition', Icon:Utensils},
    {id:'doctors', label:language==='hi'?'डॉक्टर':language==='mr'?'डॉक्टर':'Doctors', Icon:Stethoscope},
  ];
  const links = tabs.map(({id,label,Icon})=><button key={id} onClick={()=>onSelectTab(id)} aria-current={activeTab===id?'page':undefined} className={`min-w-0 flex flex-col sm:flex-row items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold ${activeTab===id?'text-clarity-teal bg-clarity-mint':'text-clarity-muted hover:bg-clarity-ivory'}`}><Icon size={20} aria-hidden="true"/><span className="min-w-0 max-w-full [overflow-wrap:anywhere]">{label}</span></button>);
  return <>
    <header className="bg-white border-b border-clarity-border sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 sm:px-8 min-h-20 py-3 flex flex-wrap items-center justify-between gap-3">
        <button onClick={()=>onSelectTab('home')} className="flex items-center gap-2 text-clarity-charcoal font-bold text-xl tracking-tight" aria-label="MediInsight"><Activity className="text-clarity-teal" aria-hidden="true" size={28}/><span className="text-left"><span className="block">MediInsight<span className="text-clarity-teal">.</span></span><span lang="en" className="block text-[10px] leading-tight font-medium tracking-normal text-clarity-muted">{t.tagline}</span></span></button>
        <nav className="hidden lg:flex gap-1" aria-label={language==='en'?'Main navigation':language==='hi'?'मुख्य नेविगेशन':'मुख्य नेव्हिगेशन'}>{links}</nav>
        <div className="flex items-center gap-1 sm:gap-3">
          <div role="group" className="flex rounded-xl bg-clarity-ivory p-1" aria-label={t.preferredLanguage}>
            {[['en','EN'],['hi','हिं'],['mr','मरा']].map(([code,label])=><button key={code} onClick={()=>onSelectLanguage?.(code)} aria-pressed={language===code} lang={code} className={`px-2 text-xs font-bold rounded-lg ${language===code?'bg-clarity-charcoal text-white':'text-clarity-muted'}`}>{label}</button>)}
          </div>
          <button onClick={()=>onSelectTab('profile')} aria-label={t.profile} aria-current={activeTab==='profile'?'page':undefined} className="p-2 text-clarity-muted rounded-full hover:bg-clarity-ivory"><UserRound size={21} aria-hidden="true"/></button>
        </div>
      </div>
    </header>
    <nav className="lg:hidden fixed bottom-0 inset-x-0 z-40 grid grid-cols-4 bg-white border-t border-clarity-border px-2 pt-2 pb-[max(8px,env(safe-area-inset-bottom))]" aria-label={language==='en'?'Main navigation':language==='hi'?'मुख्य नेविगेशन':'मुख्य नेव्हिगेशन'}>{links}</nav>
  </>;
}
