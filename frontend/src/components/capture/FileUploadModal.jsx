import React, { useRef, useState } from 'react';
import { useDialogFocus } from '../common/useDialogFocus';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function FileUploadModal({ isOpen, onClose, onFileSelected, language = 'en' }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const dialogRef = useDialogFocus(isOpen, onClose);
  if (!isOpen) return null;

  const validateAndPass = (file) => {
    setErrorMessage(null);
    if (!file) return;

    const allowed = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
    const ext = file.name.split('.').pop().toLowerCase();
    const validExts = ['pdf', 'jpg', 'jpeg', 'png', 'webp'];

    if (!allowed.includes(file.type) && !validExts.includes(ext)) {
      setErrorMessage(language==='hi'?'PDF, JPG, PNG या WEBP फ़ाइल चुनें।':language==='mr'?'PDF, JPG, PNG किंवा WEBP फाइल निवडा.':'Please select a PDF or image file (JPG, PNG, WEBP).');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage(language==='hi'?'फ़ाइल बहुत बड़ी है। अधिकतम आकार 15 MB है।':language==='mr'?'फाइल खूप मोठी आहे. कमाल आकार 15 MB आहे.':'The selected file is too large. Maximum size is 15 MB.');
      return;
    }

    onFileSelected(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndPass(e.dataTransfer.files[0]);
    }
  };

  return (
    <div ref={dialogRef} role="dialog" aria-modal="true" aria-label={t.uploadButton} tabIndex={-1} className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-clarity-charcoal/40 backdrop-blur-sm">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-lg w-full p-6 sm:p-8 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
            {t.uploadButton}
          </h2>
          <button
            onClick={onClose}
            className="text-clarity-muted hover:text-clarity-charcoal p-1 rounded-full hover:bg-clarity-ivory"
            aria-label={language==='hi'?'बंद करें':language==='mr'?'बंद करा':'Close dialog'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {errorMessage && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-xs sm:text-sm text-[#9E3624] flex items-start gap-2">
            <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span role="alert">{errorMessage}</span>
          </div>
        )}

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInputRef.current?.click(); } }}
          className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-clarity-teal bg-clarity-mint/10'
              : 'border-clarity-border hover:border-clarity-teal/50 bg-clarity-ivory/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,image/png,image/jpeg,image/webp"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                validateAndPass(e.target.files[0]);
              }
            }}
          />

          <div className="w-12 h-12 rounded-2xl bg-clarity-mint/40 text-clarity-teal flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <p className="font-semibold text-clarity-teal mb-1">
            {language === 'hi' ? 'अपनी फ़ाइल यहाँ खींचें, या ब्राउज़ करें' : language === 'mr' ? 'येथे फाईल ड्रॅग करा किंवा निवडा' : 'Drag & drop your report here, or browse'}
          </p>
          <p className="text-xs text-clarity-muted">
            PDF, JPG, PNG, WEBP (15MB max)
          </p>
        </div>

        <div className="mt-6 flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            {language === 'hi' ? 'रद्द करें' : language === 'mr' ? 'रद्द करा' : 'Cancel'}
          </Button>
        </div>
      </div>
    </div>
  );
}
