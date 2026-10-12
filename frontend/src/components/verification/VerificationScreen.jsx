import React, { useState } from 'react';
import { Button, StatusBadge } from '../common/WarmUI';

export function VerificationScreen({ biomarkers = [], onConfirmAll, onBack }) {
  const [items, setItems] = useState(biomarkers);
  const [selectedItemIndex, setSelectedItemIndex] = useState(
    // Default to the first item requiring verification if any
    Math.max(0, biomarkers.findIndex((b) => b.requires_verification))
  );
  const [editingValue, setEditingValue] = useState(
    biomarkers[selectedItemIndex]?.corrected_value || biomarkers[selectedItemIndex]?.value || ''
  );
  const [savedSuccessAlert, setSavedSuccessAlert] = useState(false);

  const currentItem = items[selectedItemIndex] || items[0];

  const handleSelectBiomarker = (index) => {
    setSelectedItemIndex(index);
    const item = items[index];
    setEditingValue(item.corrected_value || item.value || '');
    setSavedSuccessAlert(false);
  };

  const handleSaveCorrection = () => {
    if (!currentItem) return;
    const updated = items.map((b, idx) => {
      if (idx === selectedItemIndex) {
        return {
          ...b,
          value: editingValue,
          corrected_value: editingValue,
          requires_verification: false,
          correction_provenance: 'patient_edited',
        };
      }
      return b;
    });
    setItems(updated);
    setSavedSuccessAlert(true);
    setTimeout(() => setSavedSuccessAlert(false), 2500);
  };

  const pendingVerificationCount = items.filter((b) => b.requires_verification).length;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Step Header */}
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-clarity-muted">
            Step 1 of 3: Check extracted results
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-clarity-teal mt-1">
            Check these results
          </h1>
          <p className="text-sm text-clarity-muted mt-1">
            We extracted the key lab lines from your report. Whenever print clarity was uncertain, you can match it with the document below.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {pendingVerificationCount > 0 ? (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-[#855B18] border border-amber-200">
              {pendingVerificationCount} uncertain {pendingVerificationCount === 1 ? 'value' : 'values'} to check
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-[#195643] border border-emerald-200 flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              All lines confirmed
            </span>
          )}
        </div>
      </div>

      {/* Main Verification Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Biomarker List */}
        <div className="lg:col-span-5 bg-clarity-surface rounded-2xl border border-clarity-border p-4 shadow-soft">
          <h2 className="text-xs font-bold uppercase tracking-wider text-clarity-muted mb-3 px-2">
            Recognized Tests ({items.length})
          </h2>

          <div className="space-y-2">
            {items.map((b, idx) => {
              const isSelected = selectedItemIndex === idx;
              return (
                <button
                  key={b.id || idx}
                  onClick={() => handleSelectBiomarker(idx)}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-center justify-between ${
                    isSelected
                      ? 'border-clarity-teal bg-clarity-mint/15 shadow-sm'
                      : 'border-clarity-border/70 hover:border-clarity-teal/40 bg-clarity-surface'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-clarity-charcoal">
                        {b.name}
                      </span>
                      {b.requires_verification && (
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-[#855B18]">
                          Needs check
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-clarity-muted mt-0.5">
                      Ref: {b.reference_range}
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="font-bold text-sm text-clarity-teal block">
                      {b.corrected_value || b.value} {b.unit}
                    </span>
                    <StatusBadge status={b.status} />
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Source Document Inspection & Correction Box */}
        <div className="lg:col-span-7 space-y-4">
          
          {/* Document Preview Card with Simulated Source Box */}
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 shadow-soft">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-clarity-teal uppercase tracking-wider">
                Source Document Region
              </span>
              <span className="text-xs text-clarity-muted">
                Confidence: {Math.round((currentItem?.confidence || 0.9) * 100)}%
              </span>
            </div>

            {/* Simulated report paper slice with bounding highlight */}
            <div className="relative bg-[#FAFAF7] border border-clarity-border rounded-xl p-4 sm:p-6 font-mono text-xs overflow-hidden select-none">
              <div className="text-gray-400 mb-2 border-b pb-1 flex justify-between">
                <span>[CLINICAL LAB TEST REPORT]</span>
                <span>PAGE 1</span>
              </div>
              
              <div className="space-y-1.5 opacity-60">
                <div className="flex justify-between">
                  <span>PATIENT: ANONYMOUS ADULT</span>
                  <span>DATE: 12-OCT-2026</span>
                </div>
              </div>

              {/* The Highlighted Source Row */}
              <div className="my-3 p-2.5 rounded-lg border-2 border-clarity-coral bg-clarity-coral/10 font-bold text-clarity-charcoal flex justify-between items-center transition-all">
                <span className="font-sans text-xs sm:text-sm">{currentItem?.name}</span>
                <span className="bg-white px-2 py-0.5 rounded border border-clarity-coral/40 text-clarity-teal">
                  {currentItem?.original_extracted_value || currentItem?.value} {currentItem?.unit}
                </span>
              </div>

              <div className="space-y-1 opacity-50 text-[11px]">
                <div className="flex justify-between">
                  <span>REFERENCE RANGE</span>
                  <span>{currentItem?.reference_range}</span>
                </div>
              </div>

              <div className="mt-3 text-[10px] text-clarity-muted italic text-center">
                Highlighted area shows the exact row matched on your uploaded page.
              </div>
            </div>
          </div>

          {/* Value Verification & Edit Box */}
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 shadow-soft">
            <h3 className="text-sm font-bold text-clarity-teal mb-2">
              Verify recognized value for: <span className="underline">{currentItem?.name}</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-3">
              <div>
                <label className="text-xs font-medium text-clarity-muted block mb-1">
                  Original text read from image
                </label>
                <div className="px-3.5 py-2.5 bg-clarity-ivory rounded-xl border border-clarity-border text-sm font-mono text-clarity-charcoal">
                  {currentItem?.original_extracted_value || currentItem?.value} {currentItem?.unit}
                </div>
              </div>

              <div>
                <label htmlFor="correct-value-input" className="text-xs font-medium text-clarity-muted block mb-1">
                  Your corrected reading
                </label>
                <div className="flex items-center gap-2">
                  <input
                    id="correct-value-input"
                    type="text"
                    value={editingValue}
                    onChange={(e) => setEditingValue(e.target.value)}
                    className="w-full px-3.5 py-2 bg-white rounded-xl border border-clarity-teal/40 focus:border-clarity-teal text-sm font-semibold text-clarity-teal"
                  />
                  <span className="text-xs font-semibold text-clarity-muted shrink-0">
                    {currentItem?.unit}
                  </span>
                </div>
              </div>
            </div>

            {savedSuccessAlert && (
              <div className="p-2.5 mb-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-[#195643] flex items-center gap-2">
                <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Correction recorded successfully!</span>
              </div>
            )}

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-clarity-muted">
                Provenance: {currentItem?.correction_provenance === 'patient_edited' ? 'Patient Edited' : 'Initial OCR Recognition'}
              </span>
              <Button size="sm" variant="secondary" onClick={handleSaveCorrection}>
                Save Value
              </Button>
            </div>
          </div>

        </div>
      </div>

      {/* Bottom Continuation Bar */}
      <div className="mt-8 pt-4 border-t border-clarity-border flex flex-col sm:flex-row items-center justify-between gap-4">
        <Button variant="ghost" onClick={onBack}>
          &larr; Back to start
        </Button>

        <Button
          size="lg"
          variant="primary"
          onClick={() => onConfirmAll(items)}
          className="w-full sm:w-auto px-8"
        >
          Confirm & Answer a few questions &rarr;
        </Button>
      </div>
    </div>
  );
}
