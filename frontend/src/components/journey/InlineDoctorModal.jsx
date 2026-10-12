import React, { useState } from 'react';
import { Button } from '../common/WarmUI';

export function InlineDoctorModal({ isOpen, onClose }) {
  const [selectedCity, setSelectedCity] = useState('All Cities');
  const [bookedStatus, setBookedStatus] = useState(null);

  if (!isOpen) return null;

  const demoDoctors = [
    {
      id: 'doc_01',
      name: 'Dr. Ananya Sharma, MD',
      specialty: 'General Physician & Internal Medicine',
      city: 'Mumbai',
      experience: '14 years',
      modes: 'In-Person & Video',
      slots: ['Tomorrow at 10:00 AM', 'Tomorrow at 02:30 PM']
    },
    {
      id: 'doc_02',
      name: 'Dr. Rajesh Kulkarni, MD, DM',
      specialty: 'Endocrinologist / Diabetologist',
      city: 'Pune',
      experience: '18 years',
      modes: 'Video Consultation',
      slots: ['Wednesday at 04:00 PM', 'Friday at 10:30 AM']
    },
    {
      id: 'doc_03',
      name: 'Dr. Priya Nair, MD',
      specialty: 'Preventive Cardiology',
      city: 'Bangalore',
      experience: '11 years',
      modes: 'In-Person',
      slots: ['Thursday at 03:00 PM']
    }
  ];

  const filtered = selectedCity === 'All Cities'
    ? demoDoctors
    : demoDoctors.filter((d) => d.city === selectedCity);

  const handleBookSlot = (docName, slot) => {
    setBookedStatus(`Appointment reserved with ${docName} for ${slot} (Development Demo Booking)`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-clarity-charcoal/50 backdrop-blur-sm animate-in fade-in">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-2xl w-full p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-100 text-[#855B18] text-[10px] font-bold uppercase tracking-wider mb-1">
              Development Demo Directory
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
              Find the Right Doctor
            </h2>
            <p className="text-xs text-clarity-muted">
              Specialties matched to your blood test results.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-clarity-muted hover:text-clarity-charcoal p-1.5 rounded-full hover:bg-clarity-ivory"
            aria-label="Close doctor discovery"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Filter */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-clarity-border">
          <span className="text-xs font-semibold text-clarity-charcoal">Filter by Location:</span>
          <select
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
            className="p-1.5 rounded-xl border border-clarity-border text-xs font-medium text-clarity-teal bg-clarity-ivory"
          >
            <option value="All Cities">All Cities</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Pune">Pune</option>
            <option value="Bangalore">Bangalore</option>
          </select>
        </div>

        {bookedStatus && (
          <div className="p-3.5 mb-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs text-[#195643] flex items-center justify-between animate-in fade-in">
            <span>{bookedStatus}</span>
            <button
              onClick={() => setBookedStatus(null)}
              className="text-emerald-800 font-bold underline ml-2"
            >
              Cancel
            </button>
          </div>
        )}

        {/* Doctor Cards */}
        <div className="space-y-4 mb-6">
          {filtered.map((doc) => (
            <div
              key={doc.id}
              className="p-4 rounded-2xl border border-clarity-border bg-clarity-ivory/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm text-clarity-teal">{doc.name}</h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                    Verified Profile
                  </span>
                </div>
                <p className="text-xs font-medium text-clarity-charcoal mt-0.5">{doc.specialty}</p>
                <div className="text-[11px] text-clarity-muted mt-1">
                  {doc.city} &bull; {doc.experience} &bull; {doc.modes}
                </div>
              </div>

              <div className="flex flex-col gap-1.5 shrink-0">
                <span className="text-[10px] font-bold text-clarity-muted uppercase">Select Demo Slot</span>
                <div className="flex flex-wrap gap-1.5">
                  {doc.slots.map((s, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleBookSlot(doc.name, s)}
                      className="px-2.5 py-1 rounded-lg border border-clarity-teal/40 bg-white hover:bg-clarity-mint/20 text-xs font-medium text-clarity-teal transition-all"
                    >
                      {s.split(' at ')[1] || s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            Back to report
          </Button>
        </div>
      </div>
    </div>
  );
}
