import { apiFetch } from '../../api';
import React, { useState } from 'react';
import { Button, StatusBadge } from '../common/WarmUI';

export function VerificationScreen({
  biomarkers = [],
  reportId,
  onConfirmAll,
  onBack
}) {
  const [items, setItems] = useState(biomarkers);
  
  // Filter for uncertain results (requires_verification === true)
  // But allow toggling to see all results if desired
  const [showAllResults, setShowAllResults] = useState(false);
  
  const uncertainItems = items.filter((b) => b.requires_verification);
  const displayedItems = showAllResults || uncertainItems.length === 0 ? items : uncertainItems;

  const [currentIndex, setCurrentIndex] = useState(0);
  const currentItem = displayedItems[currentIndex] || items[0];

  const [editingValue, setEditingValue] = useState(
    currentItem?.corrected_value || currentItem?.value || ''
  );
  const [zoomLevel, setZoomLevel] = useState(1);
  const [savedSuccessAlert, setSavedSuccessAlert] = useState(false);

  // Sync edit input when current item changes
  const handleSelectIndex = (idx) => {
    setCurrentIndex(idx);
    const item = displayedItems[idx];
    setEditingValue(item?.corrected_value || item?.value || '');
    setSavedSuccessAlert(false);
  };

  // Confirm reading as correct
  const handleConfirmItem = async () => {
    if (!currentItem) return;
    await updateItemValue(currentItem.id, editingValue, 'patient_confirmed');
  };

  // Correct reading
  const handleCorrectItem = async () => {
    if (!currentItem) return;
    await updateItemValue(currentItem.id, editingValue, 'patient_edited');
  };

  // Skip / cannot verify option
  const handleSkipItem = () => {
    // Keep marked as needs review, advance to next
    if (currentIndex < displayedItems.length - 1) {
      handleSelectIndex(currentIndex + 1);
    }
  };

  const updateItemValue = async (bioId, val, provenance) => {
    const updated = items.map((b) => {
      if (b.id === bioId) {
        return {
          ...b,
          value: val,
          corrected_value: val,
          requires_verification: false,
          correction_provenance: provenance,
        };
      }
      return b;
    });
    setItems(updated);

    // Call backend verify endpoint if reportId exists
    if (reportId) {
      try {
        await apiFetch(`/api/v1/reports/${reportId}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            biomarker_id: bioId,
            corrected_value: val,
          }),
        });
      } catch (err) {
        console.warn('Backend verify call notice:', err);
      }
    }

    setSavedSuccessAlert(true);
    setTimeout(() => setSavedSuccessAlert(false), 2000);
  };

  const remainingUncertainCount = items.filter((b) => b.requires_verification).length;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Calm, patient-first header */}
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-clarity-muted">
            Step 1 of 3: Check extracted results
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold text-clarity-teal mt-1">
            Let's check a few details
          </h1>
          <p className="text-sm text-clarity-muted mt-1 max-w-xl">
            We couldn't read some numbers clearly. Please check them against your report.
          </p>
        </div>

        {/* Status pill & toggle */}
        <div className="flex flex-col sm:items-end gap-1.5">
          {remainingUncertainCount > 0 ? (
            <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-amber-50 text-[#855B18] border border-amber-200">
              {remainingUncertainCount} uncertain {remainingUncertainCount === 1 ? 'number' : 'numbers'} to check
            </span>
          ) : (
            <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-[#195643] border border-emerald-200 flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              All readings confirmed
            </span>
          )}

          <button
            onClick={() => {
              setShowAllResults(!showAllResults);
              setCurrentIndex(0);
            }}
            className="text-xs text-clarity-teal hover:underline font-medium"
          >
            {showAllResults ? 'Show only uncertain lines' : `View all ${items.length} recognized lines`}
          </button>
        </div>
      </div>

      {/* Main Verification Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Progress & Test Selector */}
        <div className="lg:col-span-4 bg-clarity-surface rounded-2xl border border-clarity-border p-4 shadow-soft flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-3 px-1">
              <span className="text-xs font-bold uppercase tracking-wider text-clarity-muted">
                Items to check
              </span>
              <span className="text-xs font-bold text-clarity-teal">
                {currentIndex + 1} of {displayedItems.length}
              </span>
            </div>

            <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
              {displayedItems.map((b, idx) => {
                const isSelected = currentIndex === idx;
                return (
                  <button
                    key={b.id || idx}
                    onClick={() => handleSelectIndex(idx)}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex items-center justify-between ${
                      isSelected
                        ? 'border-clarity-teal bg-clarity-mint/20 shadow-xs'
                        : 'border-clarity-border/70 hover:border-clarity-teal/40 bg-white'
                    }`}
                  >
                    <div>
                      <div className="font-semibold text-sm text-clarity-charcoal">
                        {b.name}
                      </div>
                      <div className="text-xs text-clarity-muted mt-0.5">
                        Ref: {b.reference_range}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-sm text-clarity-teal block">
                        {b.corrected_value || b.value}
                      </span>
                      {b.requires_verification ? (
                        <span className="text-[10px] font-bold text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">
                          Check
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                          Ready
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Stepper Buttons */}
          <div className="flex justify-between items-center pt-4 border-t border-clarity-border mt-3">
            <Button
              size="sm"
              variant="secondary"
              disabled={currentIndex === 0}
              onClick={() => handleSelectIndex(currentIndex - 1)}
            >
              &larr; Previous
            </Button>
            <Button
              size="sm"
              variant="secondary"
              disabled={currentIndex >= displayedItems.length - 1}
              onClick={() => handleSelectIndex(currentIndex + 1)}
            >
              Next &rarr;
            </Button>
          </div>
        </div>

        {/* Right Column: Source Comparison & Correction */}
        <div className="lg:col-span-8 space-y-4">
          
          {/* Document Preview with Zoom and Highlight */}
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 shadow-soft">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-clarity-teal uppercase tracking-wider">
                Document Preview
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setZoomLevel((z) => Math.max(0.8, z - 0.2))}
                  className="px-2 py-0.5 rounded bg-clarity-ivory border text-xs font-bold hover:bg-clarity-border"
                  title="Zoom Out"
                >
                  -
                </button>
                <span className="text-xs text-clarity-muted">{Math.round(zoomLevel * 100)}%</span>
                <button
                  onClick={() => setZoomLevel((z) => Math.min(2.0, z + 0.2))}
                  className="px-2 py-0.5 rounded bg-clarity-ivory border text-xs font-bold hover:bg-clarity-border"
                  title="Zoom In"
                >
                  +
                </button>
              </div>
            </div>

            {/* Document simulated paper preview */}
            <div className="relative bg-[#FAFAF7] border border-clarity-border rounded-xl p-4 sm:p-6 overflow-hidden select-none transition-transform" style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }}>
              <div className="text-gray-400 mb-2 border-b pb-1 font-mono text-xs flex justify-between">
                <span>[CLINICAL LAB REPORT]</span>
                <span>ORIGINAL SCAN</span>
              </div>

              {/* Exact Document Source Box or Honest Page Preview */}
              {currentItem?.source_box ? (
                <div className="my-3 p-3 rounded-lg border-2 border-clarity-coral bg-clarity-coral/10 font-bold text-clarity-charcoal flex justify-between items-center transition-all">
                  <span className="text-sm">{currentItem?.name}</span>
                  <span className="bg-white px-2.5 py-1 rounded border border-clarity-coral text-base font-bold text-clarity-teal">
                    {currentItem?.original_extracted_value || currentItem?.value} {currentItem?.unit}
                  </span>
                </div>
              ) : (
                <div className="my-3 p-3 bg-amber-50 rounded-lg text-xs text-amber-800 border border-amber-200">
                  Exact coordinates for this row are not available on this page. Please refer to your printed sheet.
                </div>
              )}

              <div className="text-[11px] font-mono text-clarity-muted mt-2">
                Reference Range: {currentItem?.reference_range}
              </div>
            </div>
          </div>

          {/* Large, Touch-Friendly Correction Controls */}
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-5 shadow-soft">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <h3 className="text-base font-bold text-clarity-teal">
                Verify measurement for <span className="underline">{currentItem?.name}</span>
              </h3>
              <StatusBadge status={currentItem?.status} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-3">
              <div>
                <label className="text-xs font-medium text-clarity-muted block mb-1">
                  Recognized reading from image
                </label>
                <div className="px-4 py-3 bg-clarity-ivory rounded-xl border border-clarity-border text-lg font-bold text-clarity-charcoal">
                  {currentItem?.original_extracted_value || currentItem?.value} {currentItem?.unit}
                </div>
              </div>

              <div>
                <label htmlFor="correct-reading-input" className="text-xs font-medium text-clarity-muted block mb-1">
                  Corrected value if printed differently
                </label>
                <div className="flex items-center gap-2">
                  <input
                    id="correct-reading-input"
                    type="text"
                    value={editingValue}
                    onChange={(e) => setEditingValue(e.target.value)}
                    className="w-full px-4 py-2.5 bg-white rounded-xl border-2 border-clarity-teal/50 focus:border-clarity-teal text-lg font-bold text-clarity-teal"
                  />
                  <span className="text-sm font-bold text-clarity-muted shrink-0">
                    {currentItem?.unit}
                  </span>
                </div>
              </div>
            </div>

            {savedSuccessAlert && (
              <div className="p-3 mb-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs sm:text-sm text-[#195643] flex items-center gap-2 animate-in fade-in">
                <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Recorded! Value updated for your report analysis.</span>
              </div>
            )}

            {/* Actions: Confirm / Correct / Skip */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-clarity-border">
              <button
                type="button"
                onClick={handleSkipItem}
                className="text-xs text-clarity-muted hover:text-clarity-charcoal underline"
              >
                Skip / Cannot verify now
              </button>

              <div className="flex items-center gap-3">
                <Button size="md" variant="secondary" onClick={handleConfirmItem}>
                  Confirm is correct
                </Button>
                <Button size="md" variant="primary" onClick={handleCorrectItem}>
                  Save Correction
                </Button>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Bottom Continue Bar */}
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
          Continue to Personalized Questions &rarr;
        </Button>
      </div>
    </div>
  );
}
