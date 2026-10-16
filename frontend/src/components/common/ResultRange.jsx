import React from 'react';

// Draw only two-sided, numeric laboratory intervals. Inequalities stay as text.
export function ResultRange({ item, language = 'en' }) {
  const match = String(item.reference_range || '').match(/^\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)/);
  const reading = String(item.numeric_value ?? item.value ?? '').match(/^\s*(\d+(?:\.\d+)?)(?:\s|$)/);
  if (!match || !reading) return null;
  const low = Number(match[1]), high = Number(match[2]), value = Number(reading[1]);
  if (high <= low) return null;
  const span = high - low;
  const min = Math.min(low - span / 2, value), max = Math.max(high + span / 2, value);
  const label = language === 'hi' ? 'प्रयोगशाला संदर्भ सीमा से तुलना' : language === 'mr' ? 'प्रयोगशाळा संदर्भ मर्यादेशी तुलना' : 'Measurement compared with laboratory reference interval';
  return <div className="my-5"><meter className="w-full h-4" min={min} max={max} low={low} high={high} optimum={(low+high)/2} value={value} aria-label={`${label}: ${item.value}; ${item.reference_range}`}/><div className="flex justify-between text-sm text-clarity-muted mt-2 tabular-nums"><span>{low}</span><span>{high}</span></div></div>;
}
