import React, { useState } from 'react';
import { Button } from '../common/WarmUI';

export function InlineNutritionModal({ isOpen, onClose, abnormalItems = [] }) {
  const [dietaryPref, setDietaryPref] = useState('vegetarian');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-clarity-charcoal/50 backdrop-blur-sm animate-in fade-in">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-xl w-full p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
              Everyday Food Guidance
            </h2>
            <p className="text-xs text-clarity-muted">
              Practical, balanced meal ideas relevant to your recent numbers.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-clarity-muted hover:text-clarity-charcoal p-1.5 rounded-full hover:bg-clarity-ivory"
            aria-label="Close nutrition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Dietary preference selector */}
        <div className="flex items-center gap-2 mb-6 p-1 bg-clarity-ivory rounded-xl border border-clarity-border/80">
          {['vegetarian', 'omnivore', 'vegan'].map((pref) => (
            <button
              key={pref}
              onClick={() => setDietaryPref(pref)}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold capitalize transition-all ${
                dietaryPref === pref
                  ? 'bg-clarity-teal text-white shadow-xs'
                  : 'text-clarity-muted hover:text-clarity-teal'
              }`}
            >
              {pref}
            </button>
          ))}
        </div>

        {/* Food suggestions tailored to lab context */}
        <div className="space-y-4 mb-6">
          <div className="p-4 rounded-2xl bg-clarity-mint/15 border border-clarity-mint/40">
            <h3 className="font-bold text-sm text-clarity-teal mb-1">
              Fostering Steady Energy & Blood Sugar Balance
            </h3>
            <p className="text-xs text-clarity-charcoal mb-3">
              Because your blood sugar numbers were slightly elevated, focusing on soluble fiber and clean protein helps prevent post-meal sugar surges.
            </p>
            <ul className="text-xs space-y-1.5 text-clarity-charcoal">
              <li>&bull; <strong>Wholesome Grains:</strong> Steel-cut oats, broken wheat (daliya), brown rice, whole wheat roti.</li>
              <li>&bull; <strong>Proteins:</strong> Yellow moong dal, masoor dal, chickpeas (chana), paneer or tofu.</li>
              <li>&bull; <strong>Fresh Greens:</strong> Spinach (palak), methi leaves, okra (bhindi), cucumber, and bell peppers.</li>
            </ul>
          </div>

          <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200">
            <h3 className="font-bold text-sm text-amber-900 mb-1">
              Vitamin D & Sunshine Habits
            </h3>
            <p className="text-xs text-amber-950 mb-2">
              For lower Vitamin D, pair mild morning sunlight exposure (15 mins) with fortified dairy or plant-based milks and sesame seeds (til).
            </p>
            <span className="text-[11px] text-amber-800 italic block">
              Notice: Dietary intake alone rarely replenishes significant vitamin D deficits. Discuss safe oral D3 drops with your doctor.
            </span>
          </div>
        </div>

        <div className="p-3 bg-clarity-ivory rounded-xl text-[11px] text-clarity-muted mb-6">
          <strong>Important: </strong>These suggestions are for general wellness and educational awareness. They do not replace personalized dietitian or medical therapy.
        </div>

        <div className="flex justify-end">
          <Button variant="primary" onClick={onClose}>
            Back to report
          </Button>
        </div>
      </div>
    </div>
  );
}
