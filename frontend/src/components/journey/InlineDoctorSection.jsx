import React, { useState, useEffect } from 'react';
import { useDialogFocus } from '../common/useDialogFocus';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function InlineDoctorSection({
  reportId = 'rep_demo_fixture',
  language = 'en',
  isExpanded = false,
  onToggleExpand = () => {}
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

  const bookingDialogRef = useDialogFocus(Boolean(bookingSlotFor), () => setBookingSlotFor(null));

  // Initial load
  useEffect(() => {
    let isMounted = true;
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
          if (isMounted) {
            setData(json);
            if (!selectedSpecialtyId && json.recommended_specialties?.length > 0) {
              setSelectedSpecialtyId(json.selected_specialty_id);
            }
          }
        } else {
          if (isMounted) createFallbackDoctorData();
        }
      } catch (err) {
        console.warn('Fallback loading doctors:', err);
        if (isMounted) createFallbackDoctorData();
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    if (reportId && isExpanded) {
      fetchProviders();
    }

    return () => {
      isMounted = false;
    };
  }, [reportId, language, selectedSpecialtyId, isExpanded]);

  const createFallbackDoctorData = () => {
    setData(null);
    setGeoError(language === 'hi' ? 'डॉक्टर सेवा उपलब्ध नहीं। फिर कोशिश करें।' : language === 'mr' ? 'डॉक्टर सेवा उपलब्ध नाही. पुन्हा प्रयत्न करा.' : 'Doctor service unavailable. Please try again.');
  };

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setGeoError(t.locationPermissionDenied);
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
          let url = `/api/v1/reports/${reportId}/doctors?lang=${language}&lat=${latitude}&lng=${longitude}`;
          if (selectedSpecialtyId) url += `&specialty_id=${selectedSpecialtyId}`;
          const res = await fetch(url);
          if (res.ok) {
            const json = await res.json();
            setData(json);
          } else { createFallbackDoctorData(); }
        } catch {
          createFallbackDoctorData();
        } finally {
          setLoading(false);
        }
      },
      (err) => {
        console.warn('Geolocation denied:', err);
        setGeoError(t.locationPermissionDenied);
        setLoading(false);
      },
      { timeout: 8000 }
    );
  };

  const handleManualLocationSearch = async (e) => {
    e.preventDefault();
    if (!locationInput.trim()) return;
    setLoading(true);
    try {
      let url = `/api/v1/reports/${reportId}/doctors?lang=${language}&city=${encodeURIComponent(locationInput.trim())}`;
      if (selectedSpecialtyId) url += `&specialty_id=${selectedSpecialtyId}`;
      const res = await fetch(url);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch {
      createFallbackDoctorData();
    } finally {
      setLoading(false);
    }
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

  // Direct Atomic Slot Reservation
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
    } catch {
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

  const providers = data?.providers || [];
  const selectedProvider = providers.find((p) => p.id === selectedProviderId) || providers[0];

  return (
    <section
      id="doctor-discovery-section"
      className="bg-clarity-surface rounded-3xl border border-clarity-border p-6 sm:p-8 shadow-soft mb-8 transition-all"
    >
      {/* SECTION HEADER & TOGGLE */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-clarity-border/70 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">🩺</span>
            <h2 className="text-xl sm:text-2xl font-bold text-clarity-teal">
              {t.findDoctor}
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-clarity-muted">
            {t.doctorDiscoverySubtitle}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {!isExpanded ? (
            <Button
              variant="secondary"
              size="md"
              onClick={onToggleExpand}
              className="justify-center"
            >
              {t.findDoctorAction || 'Find a Doctor Near Me'} &darr;
            </Button>
          ) : (
            <Button
              variant="secondary"
              size="sm"
              onClick={onToggleExpand}
              className="justify-center"
            >
              {language === 'hi' ? 'छिपाएं' : language === 'mr' ? 'लपवा' : 'Minimize'} &uarr;
            </Button>
          )}
        </div>
      </div>

      {data?.is_demo_mode && <p className="text-amber-900 bg-amber-50 rounded-xl p-4 mb-5">{language === 'hi' ? 'डेमो डॉक्टर और समय। वास्तविक बुकिंग नहीं।' : language === 'mr' ? 'डेमो डॉक्टर आणि वेळा. प्रत्यक्ष बुकिंग नाही.' : 'Demo providers and slots. Reservations are simulated and do not book clinical care.'}</p>}
      {/* EXPANDED CONTENT FLOW */}
      {isExpanded && (
        <div className="animate-in fade-in space-y-6">
          {/* Top Tabs: Find Doctor vs My Appointments */}
          <div className="flex items-center justify-between border-b border-clarity-border pb-3">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setActiveTab('directory')}
                className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                  activeTab === 'directory'
                    ? 'bg-clarity-teal text-white shadow-soft'
                    : 'bg-clarity-ivory text-clarity-muted hover:text-clarity-charcoal'
                }`}
              >
                {t.findDoctor}
              </button>
              <button
                type="button"
                onClick={loadMyAppointments}
                className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
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
                  type="button"
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    viewMode === 'list' ? 'bg-clarity-teal text-white shadow-xs' : 'text-clarity-muted'
                  }`}
                >
                  {t.listViewToggle}
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('map')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    viewMode === 'map' ? 'bg-clarity-teal text-white shadow-xs' : 'text-clarity-muted'
                  }`}
                >
                  📍 {t.mapViewToggle}
                </button>
              </div>
            )}
          </div>

          {/* DIRECTORY VIEW */}
          {activeTab === 'directory' && (
            <div className="space-y-6 animate-in fade-in">
              {/* Urgent Warning if red flag symptom detected */}
              {data?.recommended_specialties?.find((r) => r.urgent_warning) && (
                <div className="p-4 sm:p-5 rounded-2xl bg-red-50 border border-red-300 text-[#9E3624] flex items-start gap-3 shadow-soft">
                  <span className="text-xl shrink-0 mt-0.5">⚠️</span>
                  <div className="text-xs sm:text-sm leading-relaxed font-semibold">
                    {data.recommended_specialties.find((r) => r.urgent_warning).urgent_warning}
                  </div>
                </div>
              )}

              {/* SECTION: WHY THIS KIND OF DOCTOR? (RATIONALE CARD) */}
              {data?.recommended_specialties?.length > 0 && (
                <div className="p-5 sm:p-6 rounded-2xl bg-clarity-mint/15 border border-clarity-mint/40">
                  <div className="text-xs font-bold uppercase tracking-wider text-clarity-teal mb-3">
                    {t.whySuggestingSpecialty || 'Why might this kind of doctor help?'}
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {data.recommended_specialties.map((spec) => (
                      <button
                        key={spec.specialty_id}
                        type="button"
                        onClick={() => setSelectedSpecialtyId(spec.specialty_id)}
                        className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                          selectedSpecialtyId === spec.specialty_id
                            ? 'bg-clarity-teal text-white shadow-soft'
                            : 'bg-white border border-clarity-border text-clarity-charcoal hover:border-clarity-teal'
                        }`}
                      >
                        {spec.specialty_name} {spec.is_fallback ? `(${language === 'hi' ? 'प्राथमिक' : language === 'mr' ? 'प्राथमिक' : 'Holistic Entry'})` : ''}
                      </button>
                    ))}
                  </div>

                  {/* Active Specialty Medical Rationale Explanation */}
                  {data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId) && (
                    <div className="text-xs sm:text-sm text-clarity-charcoal leading-relaxed bg-white/80 p-4 rounded-xl border border-clarity-border/60">
                      <strong className="text-clarity-teal">{language === 'hi' ? 'चिकित्सीय कारण: ' : language === 'mr' ? 'वैद्यकीय कारण: ' : 'Why this care is suggested: '}</strong>
                      {data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId).why_suggesting}
                      {data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId).observed_finding && (
                        <span className="block mt-1.5 text-xs text-clarity-muted">
                          {language === 'hi' ? 'आपकी प्रयोगशाला रिपोर्ट से संबंधित: ' : language === 'mr' ? 'तुमच्या चाचणी निकालाशी संबंधित: ' : 'Based on observed report reading: '}
                          <strong className="text-clarity-charcoal font-medium">{data.recommended_specialties.find((s) => s.specialty_id === selectedSpecialtyId).observed_finding}</strong>
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* SECTION: LOCATION CONTROLS & RESOLUTION */}
              <div className="p-4 sm:p-5 rounded-2xl bg-clarity-ivory/60 border border-clarity-border flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <Button size="sm" variant="secondary" onClick={handleUseMyLocation}>
                    📍 {t.useMyLocation}
                  </Button>
                  {data?.resolved_location && (
                    <div className="text-xs">
                      <span className="text-clarity-muted">{language === 'hi' ? 'वर्तमान क्षेत्र: ' : language === 'mr' ? 'सध्याचे क्षेत्र: ' : 'Current area: '}</span>
                      <strong className="text-clarity-teal">{data.resolved_location.display_name}</strong>
                    </div>
                  )}
                </div>

                <form onSubmit={handleManualLocationSearch} className="flex flex-wrap items-center gap-2">
                  <input
                    type="text"
                    value={locationInput}
                    onChange={(e) => setLocationInput(e.target.value)}
                    placeholder={t.locationPlaceholder}
                    aria-label={t.locationPlaceholder}
                    className="p-2 px-3.5 rounded-xl border border-clarity-border text-xs sm:text-sm text-clarity-charcoal bg-white focus:outline-none focus:border-clarity-teal min-w-0 flex-1 w-full sm:w-64"
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

              {/* BOOKING CONFIRMATION NOTIFICATION */}
              {bookingSuccessNotice && (
                <div className="p-4 sm:p-5 rounded-2xl bg-emerald-50 border border-emerald-300 text-emerald-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-in fade-in">
                  <div>
                    <h4 className="font-bold text-sm sm:text-base text-[#195643] flex items-center gap-2">
                      <span>✓</span> {bookingSuccessNotice?.is_demo ? (language === 'hi' ? 'डेमो आरक्षण' : language === 'mr' ? 'डेमो आरक्षण' : 'Simulated reservation') : t.appointmentConfirmedTitle}
                    </h4>
                    <p className="text-xs sm:text-sm text-emerald-900 mt-0.5">
                      {bookingSuccessNotice.doctor_name} ({bookingSuccessNotice.clinic_name}) &bull; <strong>{bookingSuccessNotice.slot}</strong>
                    </p>
                    <span className="text-xs font-mono font-bold text-emerald-800">
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
                  <div className="bg-clarity-ivory rounded-2xl p-6 border border-clarity-border">
                    <h3 className="text-2xl font-bold mb-3">{language === 'hi' ? 'मानचित्र और दिशाएँ' : language === 'mr' ? 'नकाशा आणि दिशा' : 'Map and directions'}</h3>
                    <p className="text-clarity-muted mb-4">{language === 'hi' ? 'यहाँ लाइव मानचित्र कॉन्फ़िगर नहीं है। सत्यापित स्थान के लिए बाहरी मानचित्र खोलें।' : language === 'mr' ? 'येथे थेट नकाशा कॉन्फिगर केलेला नाही. स्थानासाठी बाह्य नकाशा उघडा.' : 'An embedded live map is not configured. Open a provider’s location in your maps app.'}</p>
                    <div className="flex flex-wrap gap-3">{providers.map(provider => <button key={provider.id} onClick={() => setSelectedProviderId(provider.id)} aria-pressed={selectedProvider?.id === provider.id} className="bg-white border border-clarity-border rounded-xl px-4 py-3">{provider.name}</button>)}</div>
                  </div>

                  {/* Focused Provider Card for Selected Map Marker */}
                  {selectedProvider && (
                    <div className="p-5 rounded-2xl bg-white border border-clarity-teal shadow-soft">
                      <div className="flex flex-col sm:flex-row justify-between items-start gap-2">
                        <div>
                          <h4 className="font-bold text-base text-clarity-teal">
                            {selectedProvider.name}
                          </h4>
                          <p className="text-xs sm:text-sm text-clarity-charcoal font-medium">
                            {selectedProvider.clinic_name} &bull; {selectedProvider.specialty}
                          </p>
                          <p className="text-xs text-clarity-muted mt-1">
                            📍 {selectedProvider.address}
                          </p>
                        </div>
                        <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                          {selectedProvider.verification_status === 'verified' ? t.verifiedClinic : t.sourceListed}
                        </span>
                      </div>

                      {/* Prominent Action Buttons: Call, WhatsApp, Directions */}
                      <div className="mt-4 pt-3 border-t border-clarity-border/60 flex flex-wrap gap-2.5">
                        {selectedProvider.phone_available && (
                          <a
                            href={`tel:${selectedProvider.phone.replace(/[^0-9+]/g, '')}`}
                            className="px-4 py-2 rounded-xl bg-clarity-teal text-white text-xs font-semibold hover:bg-clarity-teal/90 transition-all flex items-center gap-1.5"
                          >
                            📞 {t.callClinic}
                          </a>
                        )}
                        {selectedProvider.whatsapp_verified && (
                          <a
                            href={`https://wa.me/${selectedProvider.whatsapp_number.replace(/[^0-9]/g, '')}?text=${encodeURIComponent('Hello, I would like to enquire about an appointment. Could you share your availability?')}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 transition-all flex items-center gap-1.5"
                          >
                            💬 {t.whatsAppClinic}
                          </a>
                        )}
                        <a
                          href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(selectedProvider.address)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 rounded-xl bg-clarity-ivory border border-clarity-border text-clarity-charcoal text-xs font-semibold hover:bg-clarity-mint/20 transition-all flex items-center gap-1.5"
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
                          <div className="flex flex-wrap items-center gap-2">
                            <h4 className="font-bold text-sm sm:text-base text-clarity-charcoal">
                              {doc.name}
                            </h4>
                            <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                              doc.verification_status === 'verified'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-slate-100 text-slate-700'
                            }`}>
                              {doc.verification_status === 'verified' ? t.verifiedClinic : t.sourceListed}
                            </span>
                            {doc.source === 'authorized_onboarded' && (
                              <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-clarity-mint/30 text-clarity-teal">
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
                              className="px-3.5 py-2 rounded-xl border border-clarity-border bg-clarity-ivory hover:bg-clarity-mint/20 text-xs font-semibold text-clarity-charcoal flex items-center gap-1.5"
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
                              href={`https://wa.me/${doc.whatsapp_number.replace(/[^0-9]/g, '')}?text=${encodeURIComponent('Hello, I would like to enquire about an appointment. Could you share your availability?')}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-3.5 py-2 rounded-xl border border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-xs font-semibold text-emerald-800 flex items-center gap-1.5"
                            >
                              💬 {t.whatsAppClinic}
                            </a>
                          )}

                          <a
                            href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(doc.address)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3.5 py-2 rounded-xl border border-clarity-border bg-clarity-ivory hover:bg-clarity-mint/20 text-xs font-semibold text-clarity-charcoal flex items-center gap-1.5"
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
                      <div className="flex flex-wrap items-center gap-2">
                        <h4 className="font-bold text-sm text-clarity-charcoal">
                          {app.doctor_name}
                        </h4>
                        <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
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
                      <div className="flex flex-wrap items-center gap-2">
                        {reschedulingBookingId === app.booking_id ? (
                          <div className="flex flex-wrap items-center gap-2">
                            <input
                              type="text"
                              value={rescheduleSlot}
                              onChange={(e) => setRescheduleSlot(e.target.value)}
                              placeholder="e.g. Friday at 03:00 PM"
                              className="p-1.5 px-2.5 rounded-lg border border-clarity-border text-xs bg-white w-44"
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

          {/* MEDICAL DISCLAIMER */}
          <p className="text-[11px] text-clarity-muted leading-relaxed italic bg-clarity-ivory/50 p-3 rounded-xl border border-clarity-border/40">
            {data?.disclaimer || 'Simplifier connects you with verified clinics for educational coordination. In an emergency, proceed directly to an emergency medical department.'}
          </p>
        </div>
      )}

      {/* DIRECT BOOKING MODAL OVERLAY */}
      {bookingSlotFor && (
        <div ref={bookingDialogRef} role="dialog" aria-modal="true" aria-label={t.bookSlot} className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-clarity-charcoal/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-clarity-surface rounded-2xl border border-clarity-border p-6 max-w-md w-full shadow-elevated">
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-bold text-base text-clarity-teal">
                {t.bookSlot}
              </h4>
              <button
                type="button"
                onClick={() => setBookingSlotFor(null)}
                aria-label={language === 'hi' ? 'बंद करें' : language === 'mr' ? 'बंद करा' : 'Close'}
                className="text-clarity-muted hover:text-clarity-charcoal text-sm p-1"
              >
                ✕
              </button>
            </div>
            <p className="text-xs text-clarity-muted mb-4">
              {bookingSlotFor.name} &bull; {bookingSlotFor.clinic_name}
            </p>

            <div className="space-y-3 mb-5">
              <div>
                <label htmlFor="booking-slot" className="block text-xs font-semibold text-clarity-charcoal mb-1">
                  {t.selectSlot}
                </label>
                <select
                  id="booking-slot"
                  value={selectedSlot}
                  onChange={(e) => setSelectedSlot(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-clarity-border bg-clarity-ivory text-xs font-semibold text-clarity-charcoal focus:outline-none"
                >
                  {bookingSlotFor.available_slots?.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="patient-name" className="block text-xs font-semibold text-clarity-charcoal mb-1">
                  {language === 'hi' ? 'मरीज़ का नाम' : language === 'mr' ? 'रुग्णाचे नाव' : 'Patient name'}
                </label>
                <input
                  type="text"
                  id="patient-name"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  autoComplete="name"
                  className="w-full p-2.5 rounded-xl border border-clarity-border bg-white text-xs text-clarity-charcoal focus:outline-none focus:border-clarity-teal"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setBookingSlotFor(null)}
              >
                {language === 'hi' ? 'रद्द करें' : language === 'mr' ? 'रद्द करा' : 'Cancel'}
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleConfirmDirectBooking}
                disabled={bookingLoading}
              >
                {bookingLoading ? t.readingReport : (language === 'hi' ? 'आरक्षण की पुष्टि करें' : language === 'mr' ? 'आरक्षण निश्चित करा' : 'Confirm reservation')}
              </Button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
