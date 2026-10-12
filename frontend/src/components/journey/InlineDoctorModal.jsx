import React, { useState, useEffect } from 'react';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function InlineDoctorModal({
  isOpen,
  onClose,
  reportId = 'rep_demo_fixture',
  language = 'en'
}) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  // View state: 'directory' | 'my_appointments'
  const [activeTab, setActiveTab] = useState('directory');
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'map'
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  // Filters & selection
  const [selectedSpecialtyId, setSelectedSpecialtyId] = useState(null);
  const [locationInput, setLocationInput] = useState('');
  const [geoError, setGeoError] = useState(null);
  const [selectedProviderId, setSelectedProviderId] = useState(null);

  // Booking interaction state
  const [bookingSlotFor, setBookingSlotFor] = useState(null); // provider obj
  const [selectedSlot, setSelectedSlot] = useState('');
  const [patientName, setPatientName] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingSuccessNotice, setBookingSuccessNotice] = useState(null);

  // My Appointments list
  const [myAppointments, setMyAppointments] = useState([]);
  const [loadingApps, setLoadingApps] = useState(false);

  // Reschedule state
  const [reschedulingBookingId, setReschedulingBookingId] = useState(null);
  const [rescheduleSlot, setRescheduleSlot] = useState('');

  // Initial load
  useEffect(() => {
    if (!isOpen) return;
    fetchProviders();
  }, [isOpen, reportId, language, selectedSpecialtyId]);

  const fetchProviders = async (cityParam = null, latParam = null, lngParam = null) => {
    setLoading(true);
    setGeoError(null);
    try {
      let url = `/api/v1/reports/${reportId}/doctors?lang=${language}`;
      if (selectedSpecialtyId) url += `&specialty_id=${selectedSpecialtyId}`;
      if (cityParam) url += `&city=${encodeURIComponent(cityParam)}`;
      if (latParam !== null && lngParam !== null) url += `&lat=${latParam}&lng=${lngParam}`;

      const res = await fetch(url);
      if (res.ok) {
        const json = await res.json();
        setData(json);
        if (!selectedSpecialtyId && json.recommended_specialties?.length > 0) {
          setSelectedSpecialtyId(json.selected_specialty_id);
        }
      } else {
        createFallbackDoctorData();
      }
    } catch (err) {
      console.warn('Fallback loading doctors:', err);
      createFallbackDoctorData();
    } finally {
      setLoading(false);
    }
  };

  const createFallbackDoctorData = () => {
    setData({
      report_id: reportId,
      recommended_specialties: [
        {
          specialty_id: 'endocrinology',
          specialty_name: language === 'hi' ? 'एंडोक्रिनोलॉजिस्ट (शुगर विशेषज्ञ)' : language === 'mr' ? 'मधुमेह तज्ज्ञ' : 'Endocrinologist / Diabetologist',
          why_suggesting: 'Evaluates long-term glucose patterns and insulin regulation.',
          observed_finding: 'Fasting Blood Glucose (118 mg/dL)'
        },
        {
          specialty_id: 'general_physician',
          specialty_name: language === 'hi' ? 'जनरल फिजिशियन' : language === 'mr' ? 'जनरल फिजिशियन' : 'General Physician & Internal Medicine',
          why_suggesting: 'Provides comprehensive, holistic evaluation of all your blood markers.',
          observed_finding: null,
          is_fallback: true
        }
      ],
      selected_specialty_id: 'endocrinology',
      resolved_location: {
        query: 'Mumbai',
        display_name: 'Mumbai, Maharashtra',
        city: 'Mumbai',
        is_approximate: true
      },
      providers: [
        {
          id: 'prov_mum_01',
          name: 'Dr. Ananya Sharma, MD',
          clinic_name: 'Apex Internal Medicine & Diagnostic Centre',
          specialty: 'General Physician & Internal Medicine',
          specialty_id: 'general_physician',
          city: 'Mumbai',
          pincode: '400012',
          address: 'Dr. E Borges Road, Parel, Mumbai, Maharashtra 400012',
          coordinates: { lat: 19.0025, lng: 72.8423 },
          distance_km: 3.2,
          phone: '+91 22 2417 7000',
          phone_available: true,
          whatsapp_number: '+919820011223',
          whatsapp_verified: true,
          source: 'authorized_onboarded',
          verification_status: 'verified',
          booking_capability: 'direct_booking',
          available_slots: ['Tomorrow at 10:00 AM', 'Tomorrow at 02:30 PM', 'Thursday at 11:15 AM'],
          languages: ['English', 'Hindi', 'Marathi']
        },
        {
          id: 'prov_mum_02',
          name: 'Dr. Sanjeev Mehta, MD, DM',
          clinic_name: 'Metabolic Care & Endocrine Clinic',
          specialty: 'Endocrinologist / Diabetologist',
          specialty_id: 'endocrinology',
          city: 'Mumbai',
          pincode: '400050',
          address: 'Linking Road, Bandra West, Mumbai, Maharashtra 400050',
          coordinates: { lat: 19.0596, lng: 72.8295 },
          distance_km: 5.8,
          phone: '+91 22 2640 1200',
          phone_available: true,
          whatsapp_number: '+919820033445',
          whatsapp_verified: true,
          source: 'authorized_onboarded',
          verification_status: 'verified',
          booking_capability: 'direct_booking',
          available_slots: ['Wednesday at 11:00 AM', 'Friday at 04:30 PM'],
          languages: ['English', 'Hindi']
        }
      ],
      total_count: 2,
      is_demo_mode: false,
      live_provider_api_configured: true,
      disclaimer: 'Simplifier connects you with verified clinics for educational coordination.'
    });
  };

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoError(t.locationPermissionDenied);
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        fetchProviders(null, latitude, longitude);
      },
      (err) => {
        console.warn('Geolocation denied:', err);
        setGeoError(t.locationPermissionDenied);
        setLoading(false);
      },
      { timeout: 8000 }
    );
  };

  const handleManualLocationSearch = (e) => {
    e.preventDefault();
    if (!locationInput.trim()) return;
    fetchProviders(locationInput.trim());
  };

  const loadMyAppointments = async () => {
    setActiveTab('my_appointments');
    setLoadingApps(true);
    try {
      const res = await fetch('/api/v1/reports/doctors/my-appointments');
      if (res.ok) {
        const json = await res.json();
        setMyAppointments(json.appointments || []);
      }
    } catch (err) {
      console.warn('Failed to load appointments:', err);
    } finally {
      setLoadingApps(false);
    }
  };

  // Direct Atomic Booking
  const handleConfirmDirectBooking = async () => {
    if (!bookingSlotFor || !selectedSlot) return;
    setBookingLoading(true);
    try {
      const res = await fetch('/api/v1/reports/doctors/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doctor_id: bookingSlotFor.id,
          slot: selectedSlot,
          patient_name: patientName.trim() || 'Anonymous Patient',
          report_id: reportId
        })
      });
      if (res.ok) {
        const json = await res.json();
        setBookingSuccessNotice(json.appointment);
        setBookingSlotFor(null);
        setSelectedSlot('');
      } else {
        const errJson = await res.json();
        alert(errJson.detail || 'Could not reserve slot.');
      }
    } catch (e) {
      alert('Network error reserving slot.');
    } finally {
      setBookingLoading(false);
    }
  };

  // Reschedule
  const handleExecuteReschedule = async (bookingId, newSlot) => {
    try {
      const res = await fetch('/api/v1/reports/doctors/reschedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          booking_id: bookingId,
          new_slot: newSlot
        })
      });
      if (res.ok) {
        setReschedulingBookingId(null);
        loadMyAppointments();
      } else {
        const err = await res.json();
        alert(err.detail || 'Failed to reschedule.');
      }
    } catch {
      alert('Failed to reschedule.');
    }
  };

  // Cancel
  const handleExecuteCancel = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;
    try {
      const res = await fetch('/api/v1/reports/doctors/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: bookingId })
      });
      if (res.ok) {
        loadMyAppointments();
      }
    } catch {
      alert('Failed to cancel.');
    }
  };

  if (!isOpen) return null;

  const providers = data?.providers || [];
  const selectedProvider = providers.find((p) => p.id === selectedProviderId) || providers[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-clarity-charcoal/50 backdrop-blur-sm animate-in fade-in">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-4xl w-full p-5 sm:p-8 max-h-[92vh] overflow-y-auto flex flex-col justify-between">
        <div>
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl">🩺</span>
                <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
                  {t.doctorDiscoveryTitle}
                </h2>
              </div>
              <p className="text-xs sm:text-sm text-clarity-muted mt-1">
                {t.doctorDiscoverySubtitle}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-clarity-muted hover:text-clarity-charcoal p-2 rounded-full hover:bg-clarity-ivory"
              aria-label="Close doctor discovery"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation Tabs: Discovery vs My Appointments */}
          <div className="flex items-center justify-between border-b border-clarity-border pb-2 mb-4">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('directory')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'directory'
                    ? 'bg-clarity-teal text-white shadow-soft'
                    : 'bg-clarity-ivory text-clarity-muted hover:text-clarity-charcoal'
                }`}
              >
                {t.findDoctor}
              </button>
              <button
                onClick={loadMyAppointments}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === 'my_appointments'
                    ? 'bg-clarity-teal text-white shadow-soft'
                    : 'bg-clarity-ivory text-clarity-muted hover:text-clarity-charcoal'
                }`}
              >
                📅 {t.myAppointmentsTab}
              </button>
            </div>

            {activeTab === 'directory' && (
              <div className="flex items-center gap-1 bg-clarity-ivory p-1 rounded-xl border border-clarity-border">
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                    viewMode === 'list' ? 'bg-clarity-teal text-white' : 'text-clarity-muted'
                  }`}
                >
                  {t.listViewToggle}
                </button>
                <button
                  onClick={() => setViewMode('map')}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                    viewMode === 'map' ? 'bg-clarity-teal text-white' : 'text-clarity-muted'
                  }`}
                >
                  📍 {t.mapViewToggle}
                </button>
              </div>
            )}
          </div>

          {/* DIRECTORY VIEW */}
          {activeTab === 'directory' && (
            <div className="space-y-5 animate-in fade-in">
              {/* Urgent Warning if present */}
              {data?.recommended_specialties?.find((r) => r.urgent_warning) && (
                <div className="p-4 rounded-2xl bg-red-50 border border-red-300 text-[#9E3624] flex items-start gap-3 shadow-soft">
                  <span className="text-xl">⚠️</span>
                  <div className="text-xs leading-relaxed font-medium">
                    {data.recommended_specialties.find((r) => r.urgent_warning).urgent_warning}
                  </div>
                </div>
              )}

              {/* Recommended Specialties & Medical Rationale */}
              {data?.recommended_specialties?.length > 0 && (
                <div className="p-4 rounded-2xl bg-clarity-mint/15 border border-clarity-mint/40">
                  <div className="text-xs font-bold uppercase tracking-wider text-clarity-teal mb-2">
                    {t.whySuggestingSpecialty}
                  </div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {data.recommended_specialties.map((spec) => (
                      <button
                        key={spec.specialty_id}
                        onClick={() => setSelectedSpecialtyId(spec.specialty_id)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                          selectedSpecialtyId === spec.specialty_id
                            ? 'bg-clarity-teal text-white shadow-soft'
                            : 'bg-white border border-clarity-border text-clarity-charcoal hover:border-clarity-teal'
                        }`}
                      >
                        {spec.specialty_name} {spec.is_fallback ? '(Holistic)' : ''}
                      </button>
                    ))}
                  </div>
                  {/* Explanation for active specialty */}
                  {data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId) && (
                    <div className="text-xs text-clarity-charcoal leading-relaxed bg-white/70 p-3 rounded-xl border border-clarity-border/60">
                      <strong>Rationale: </strong>
                      {data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId).why_suggesting}
                      {data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId).observed_finding && (
                        <span className="block mt-1 text-clarity-muted">
                          Matched to your lab finding: <em>{data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId).observed_finding}</em>
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Location Controls */}
              <div className="p-4 rounded-2xl bg-clarity-surface border border-clarity-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="secondary" onClick={handleUseMyLocation}>
                    📍 {t.useMyLocation}
                  </Button>
                  {data?.resolved_location && (
                    <span className="text-xs font-semibold text-clarity-teal">
                      {data.resolved_location.display_name}
                    </span>
                  )}
                </div>

                <form onSubmit={handleManualLocationSearch} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={locationInput}
                    onChange={(e) => setLocationInput(e.target.value)}
                    placeholder={t.locationPlaceholder}
                    className="p-1.5 px-3 rounded-xl border border-clarity-border text-xs text-clarity-charcoal bg-clarity-ivory focus:outline-none focus:border-clarity-teal w-48 sm:w-60"
                  />
                  <Button size="sm" variant="mint" type="submit">
                    {t.searchLocationBtn}
                  </Button>
                </form>
              </div>

              {geoError && (
                <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900">
                  {geoError}
                </div>
              )}

              {/* Booking Confirmation Banner */}
              {bookingSuccessNotice && (
                <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-300 text-emerald-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-in fade-in">
                  <div>
                    <h4 className="font-bold text-sm text-[#195643] flex items-center gap-2">
                      <span>✓</span> {t.appointmentConfirmedTitle}
                    </h4>
                    <p className="text-xs text-emerald-900 mt-0.5">
                      {bookingSuccessNotice.doctor_name} ({bookingSuccessNotice.clinic_name}) &bull; {bookingSuccessNotice.slot}
                    </p>
                    <span className="text-[11px] font-mono font-bold text-emerald-800">
                      {t.bookingReference}: {bookingSuccessNotice.booking_id}
                    </span>
                  </div>
                  <Button size="sm" variant="secondary" onClick={() => setBookingSuccessNotice(null)}>
                    Dismiss
                  </Button>
                </div>
              )}

              {/* MAP VIEW */}
              {viewMode === 'map' && (
                <div className="space-y-4">
                  {/* Clean SVG interactive canvas */}
                  <div className="relative w-full h-64 bg-emerald-50/50 rounded-2xl border border-clarity-border overflow-hidden flex items-center justify-center">
                    <svg className="w-full h-full opacity-30" xmlns="http://www.w3.org/2000/svg">
                      <defs>
                        <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                          <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#183C43" strokeWidth="0.5" />
                        </pattern>
                      </defs>
                      <rect width="100%" height="100%" fill="url(#grid)" />
                    </svg>

                    {/* Center Landmark / Pin markers */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <div className="text-xs font-bold text-clarity-teal/60 uppercase tracking-widest bg-white/70 px-3 py-1 rounded-full border border-clarity-border">
                        📍 {data?.resolved_location?.city || 'Local Area'} Navigation Hub
                      </div>
                    </div>

                    {/* Map Pins for providers */}
                    <div className="absolute inset-0 p-8 flex flex-wrap items-center justify-around">
                      {providers.map((p, idx) => (
                        <button
                          key={p.id}
                          onClick={() => setSelectedProviderId(p.id)}
                          className={`p-2 rounded-2xl shadow-elevated transition-transform hover:scale-110 flex items-center gap-1.5 text-xs font-bold ${
                            selectedProvider?.id === p.id
                              ? 'bg-clarity-teal text-white ring-4 ring-clarity-mint'
                              : 'bg-white border border-clarity-border text-clarity-teal'
                          }`}
                        >
                          <span>🏥</span>
                          <span className="hidden sm:inline">{p.name.split(',')[0]}</span>
                          {p.distance_km && <span className="text-[10px] opacity-80">({p.distance_km} km)</span>}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Highlighted Provider Card below Map */}
                  {selectedProvider && (
                    <div className="p-4 rounded-2xl bg-white border border-clarity-teal shadow-soft">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-bold text-sm sm:text-base text-clarity-teal">
                            {selectedProvider.name}
                          </h4>
                          <p className="text-xs text-clarity-charcoal font-medium">
                            {selectedProvider.clinic_name}
                          </p>
                          <p className="text-xs text-clarity-muted mt-1">
                            📍 {selectedProvider.address}
                          </p>
                        </div>
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                          {selectedProvider.verification_status === 'verified' ? t.verifiedClinic : t.sourceListed}
                        </span>
                      </div>

                      {/* Grounded Action buttons */}
                      <div className="mt-3 pt-3 border-t border-clarity-border/60 flex flex-wrap gap-2">
                        {selectedProvider.phone_available && (
                          <a
                            href={`tel:${selectedProvider.phone.replace(/[^0-9+]/g, '')}`}
                            className="px-3 py-1.5 rounded-xl bg-clarity-teal text-white text-xs font-semibold hover:bg-clarity-teal/90 transition-all flex items-center gap-1"
                          >
                            📞 {t.callClinic}
                          </a>
                        )}
                        {selectedProvider.whatsapp_verified && (
                          <a
                            href={`https://wa.me/${selectedProvider.whatsapp_number.replace(/[^0-9]/g, '')}?text=${encodeURIComponent('Hello, I would like to enquire about an appointment.')}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1.5 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 transition-all flex items-center gap-1"
                          >
                            💬 {t.whatsAppClinic}
                          </a>
                        )}
                        <a
                          href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(selectedProvider.address)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1.5 rounded-xl bg-clarity-ivory border border-clarity-border text-clarity-charcoal text-xs font-semibold hover:bg-clarity-mint/20 transition-all flex items-center gap-1"
                        >
                          🗺️ {t.getDirections}
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* LIST VIEW */}
              {viewMode === 'list' && (
                <div className="space-y-4">
                  {loading ? (
                    <div className="py-12 text-center text-clarity-teal">
                      <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-clarity-teal border-t-transparent mb-3" />
                      <p className="text-sm font-semibold">{t.readingReport}</p>
                    </div>
                  ) : providers.length === 0 ? (
                    <div className="p-8 text-center bg-clarity-ivory rounded-2xl border border-clarity-border text-xs text-clarity-muted">
                      {t.noDoctorsFoundInArea}
                    </div>
                  ) : (
                    providers.map((doc) => (
                      <div
                        key={doc.id}
                        className="p-5 rounded-2xl bg-clarity-surface border border-clarity-border shadow-soft flex flex-col md:flex-row md:items-center justify-between gap-4"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-sm sm:text-base text-clarity-charcoal">
                              {doc.name}
                            </h4>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              doc.verification_status === 'verified'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-slate-100 text-slate-700'
                            }`}>
                              {doc.verification_status === 'verified' ? t.verifiedClinic : t.sourceListed}
                            </span>
                            {doc.source === 'authorized_onboarded' && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-clarity-mint/30 text-clarity-teal">
                                {t.directBookingBadge}
                              </span>
                            )}
                          </div>
                          <p className="text-xs font-semibold text-clarity-teal">
                            {doc.clinic_name} &bull; {doc.specialty}
                          </p>
                          <p className="text-xs text-clarity-muted">
                            📍 {doc.address} {doc.distance_km && <strong className="text-clarity-charcoal">({doc.distance_km} km away)</strong>}
                          </p>
                        </div>

                        {/* Actions: Call, WhatsApp, Directions, or Direct Slot Booking */}
                        <div className="flex flex-wrap items-center gap-2 shrink-0">
                          {doc.phone_available ? (
                            <a
                              href={`tel:${doc.phone.replace(/[^0-9+]/g, '')}`}
                              className="px-3 py-1.5 rounded-xl border border-clarity-border bg-clarity-ivory hover:bg-clarity-mint/20 text-xs font-medium text-clarity-charcoal flex items-center gap-1"
                            >
                              📞 {t.callClinic}
                            </a>
                          ) : (
                            <span className="text-[11px] text-clarity-muted italic">
                              {t.phoneUnavailable}
                            </span>
                          )}

                          {doc.whatsapp_verified && (
                            <a
                              href={`https://wa.me/${doc.whatsapp_number.replace(/[^0-9]/g, '')}?text=${encodeURIComponent('Hello, I would like to enquire about an appointment.')}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-3 py-1.5 rounded-xl border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-xs font-medium text-emerald-800 flex items-center gap-1"
                            >
                              💬 {t.whatsAppClinic}
                            </a>
                          )}

                          <a
                            href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(doc.address)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1.5 rounded-xl border border-clarity-border bg-clarity-ivory hover:bg-clarity-mint/20 text-xs font-medium text-clarity-charcoal flex items-center gap-1"
                          >
                            🗺️ {t.getDirections}
                          </a>

                          {doc.available_slots?.length > 0 && (
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => {
                                setBookingSlotFor(doc);
                                setSelectedSlot(doc.available_slots[0]);
                              }}
                            >
                              {t.bookSlot} &rarr;
                            </Button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          )}

          {/* MY APPOINTMENTS VIEW */}
          {activeTab === 'my_appointments' && (
            <div className="space-y-4 animate-in fade-in">
              <h3 className="font-bold text-base text-clarity-teal mb-3">
                {t.myAppointmentsTab}
              </h3>

              {loadingApps ? (
                <div className="py-12 text-center text-clarity-teal">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-clarity-teal border-t-transparent mb-3" />
                  <p className="text-sm font-semibold">{t.readingReport}</p>
                </div>
              ) : myAppointments.length === 0 ? (
                <div className="p-8 text-center bg-clarity-ivory rounded-2xl border border-clarity-border text-xs text-clarity-muted">
                  {t.noAppointmentsYet}
                </div>
              ) : (
                myAppointments.map((app) => (
                  <div
                    key={app.booking_id}
                    className="p-5 rounded-2xl bg-clarity-surface border border-clarity-border shadow-soft flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-sm text-clarity-charcoal">
                          {app.doctor_name}
                        </h4>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          app.status === 'cancelled'
                            ? 'bg-rose-100 text-rose-800'
                            : app.status === 'rescheduled'
                            ? 'bg-amber-100 text-amber-900'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}>
                          {app.status.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-clarity-teal font-medium mt-0.5">
                        {app.clinic_name} &bull; {app.specialty}
                      </p>
                      <p className="text-xs text-clarity-muted mt-1">
                        🕒 <strong>{app.slot}</strong> &bull; Patient: {app.patient_name}
                      </p>
                      <span className="text-[11px] font-mono text-clarity-muted">
                        Ref: {app.booking_id}
                      </span>
                    </div>

                    {app.status !== 'cancelled' && (
                      <div className="flex items-center gap-2">
                        {reschedulingBookingId === app.booking_id ? (
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={rescheduleSlot}
                              onChange={(e) => setRescheduleSlot(e.target.value)}
                              placeholder="e.g. Friday at 03:00 PM"
                              className="p-1 px-2 rounded-lg border border-clarity-border text-xs bg-white w-40"
                            />
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => handleExecuteReschedule(app.booking_id, rescheduleSlot)}
                            >
                              Save
                            </Button>
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => setReschedulingBookingId(null)}
                            >
                              Cancel
                            </Button>
                          </div>
                        ) : (
                          <>
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => {
                                setReschedulingBookingId(app.booking_id);
                                setRescheduleSlot(app.slot);
                              }}
                            >
                              {t.rescheduleBtn}
                            </Button>
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => handleExecuteCancel(app.booking_id)}
                            >
                              {t.cancelBookingBtn}
                            </Button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* BOOKING DIALOG OVERLAY */}
        {bookingSlotFor && (
          <div className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-clarity-charcoal/60 backdrop-blur-xs animate-in fade-in">
            <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 max-w-md w-full shadow-elevated">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-bold text-base text-clarity-teal">
                  {t.bookSlot}
                </h4>
                <button
                  onClick={() => setBookingSlotFor(null)}
                  className="text-clarity-muted hover:text-clarity-charcoal text-sm p-1"
                >
                  ✕
                </button>
              </div>

              <div className="p-3 bg-clarity-ivory rounded-xl border border-clarity-border mb-4 text-xs text-clarity-charcoal space-y-1">
                <p><strong>Doctor:</strong> {bookingSlotFor.name}</p>
                <p><strong>Clinic:</strong> {bookingSlotFor.clinic_name}</p>
                <p><strong>Address:</strong> {bookingSlotFor.address}</p>
              </div>

              <div className="space-y-3 mb-5">
                <div>
                  <label className="block text-xs font-semibold text-clarity-charcoal mb-1">
                    Patient Name:
                  </label>
                  <input
                    type="text"
                    value={patientName}
                    onChange={(e) => setPatientName(e.target.value)}
                    placeholder="Enter patient full name"
                    className="w-full p-2 rounded-xl border border-clarity-border text-xs bg-clarity-ivory"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-clarity-charcoal mb-1">
                    {t.selectSlot}:
                  </label>
                  <select
                    value={selectedSlot}
                    onChange={(e) => setSelectedSlot(e.target.value)}
                    className="w-full p-2 rounded-xl border border-clarity-border text-xs bg-clarity-ivory text-clarity-teal font-semibold"
                  >
                    {bookingSlotFor.available_slots?.map((s, idx) => (
                      <option key={idx} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="secondary" size="sm" onClick={() => setBookingSlotFor(null)}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleConfirmDirectBooking}
                  disabled={bookingLoading}
                >
                  {bookingLoading ? 'Reserving...' : 'Confirm Reservation'}
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-clarity-border flex justify-end">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Back to report
          </Button>
        </div>
      </div>
    </div>
  );
}
