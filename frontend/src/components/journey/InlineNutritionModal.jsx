import React from 'react';
import { InlineNutritionSection } from './InlineNutritionSection';
import { useDialogFocus } from '../common/useDialogFocus';

export function InlineNutritionModal({ isOpen, onClose, reportId = 'rep_demo_fixture', language = 'en' }) {
  const dialogRef = useDialogFocus(isOpen, onClose);
  if (!isOpen) return null;
  const label = language === 'hi' ? 'बंद करें' : language === 'mr' ? 'बंद करा' : 'Close';
  return <div ref={dialogRef} role="dialog" aria-modal="true" aria-label="Nutrition" className="fixed inset-0 z-50 bg-clarity-charcoal/50 p-4 flex items-center justify-center">
    <div className="bg-clarity-ivory rounded-3xl w-full max-w-4xl max-h-[90dvh] overflow-y-auto p-4"><button onClick={onClose} aria-label="Close nutrition" className="px-4 py-2 text-clarity-teal font-bold">{label}</button><InlineNutritionSection reportId={reportId} language={language} isExpanded /></div>
  </div>;
}
