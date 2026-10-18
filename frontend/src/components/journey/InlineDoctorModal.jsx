import React from 'react';
import { InlineDoctorSection } from './InlineDoctorSection';
import { useDialogFocus } from '../common/useDialogFocus';

export function InlineDoctorModal({ isOpen, onClose, reportId = 'rep_demo_fixture', language = 'en' }) {
  const dialogRef = useDialogFocus(isOpen, onClose);
  if (!isOpen) return null;
  const label = language === 'hi' ? 'बंद करें' : language === 'mr' ? 'बंद करा' : 'Close';
  return <div ref={dialogRef} role="dialog" aria-modal="true" aria-label={language === "hi" ? "डॉक्टर" : language === "mr" ? "डॉक्टर" : "Doctor"} className="fixed inset-0 z-50 bg-clarity-charcoal/50 p-4 flex items-center justify-center">
    <div className="bg-clarity-ivory rounded-3xl w-full max-w-4xl max-h-[90dvh] overflow-y-auto p-4"><button onClick={onClose} aria-label={label} className="px-4 py-2 text-clarity-teal font-bold">{label}</button><InlineDoctorSection reportId={reportId} language={language} isExpanded /></div>
  </div>;
}
