import React, { useRef, useState, useEffect, useCallback } from 'react';
import { useDialogFocus } from '../common/useDialogFocus';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function CameraCaptureModal({ isOpen, onClose, onCompleteCapture, language = 'en' }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const videoRef = useRef(null);
  const fileFallbackRef = useRef(null);
  const streamRef = useRef(null);

  const [addingPage, setAddingPage] = useState(false);
  const [streamActive, setStreamActive] = useState(false);
  const [permissionError, setPermissionError] = useState(null);
  const [capturedPages, setCapturedPages] = useState([]);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [blurWarning, setBlurWarning] = useState(false);
  const facingMode = 'environment'; // Prefer rear-facing camera

  const startCamera = useCallback(async () => {
    setPermissionError(null);
    setBlurWarning(false);

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setPermissionError(language === 'hi' ? 'कैमरा उपलब्ध नहीं है। कृपया फ़ोटो अपलोड विकल्प का उपयोग करें।' : language === 'mr' ? 'कॅमेरा उपलब्ध नाही. कृपया फोटो अपलोड पर्याय वापरा.' : 'Live camera is not supported or requires a secure context (HTTPS/localhost). Please use the photo file picker instead.');
      return;
    }

    try {
      const constraints = {
        video: {
          facingMode: { ideal: facingMode },
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStreamActive(true);
    } catch (err) {
      console.warn('Camera access error:', err);
      setPermissionError(language === 'hi' ? 'कैमरा अनुमति अस्वीकृत या उपलब्ध नहीं। कृपया डिवाइस से फ़ोटो चुनें।' : language === 'mr' ? 'कॅमेरा परवानगी नाकारली गेली. कृपया डिव्हाइसवरून फोटो निवडा.' : 'Camera access unavailable. Please choose a photo from your device.');
      setStreamActive(false);
    }
  }, [facingMode, language]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setStreamActive(false);
  }, []);

  useEffect(() => {
    if (isOpen && capturedPages.length === 0) {
      startCamera();
    }
    return () => {
      stopCamera();
    };
  }, [isOpen, startCamera, stopCamera]);

  useEffect(() => {
    if (!isOpen) { setCapturedPages([]); setActivePageIndex(0); setPermissionError(null); setAddingPage(false); }
  }, [isOpen]);
  const dialogRef = useDialogFocus(isOpen, onClose);
  if (!isOpen) return null;

  const handleSnap = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `camera_capture_page_${capturedPages.length + 1}.jpg`, {
        type: 'image/jpeg',
      });
      const dataUrl = canvas.toDataURL('image/jpeg');

      setCapturedPages((prev) => [...prev, { file, dataUrl, pageNumber: prev.length + 1 }]);
      setActivePageIndex(capturedPages.length);
      setAddingPage(false);
      stopCamera();
    }, 'image/jpeg', 0.92);
  };

  const handleFallbackFile = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!['image/jpeg','image/png','image/webp'].includes(file.type) || file.size>15*1024*1024) {
        setPermissionError(language==='hi'?'15 MB तक की JPG, PNG या WEBP फ़ोटो चुनें।':language==='mr'?'15 MB पर्यंतचा JPG, PNG किंवा WEBP फोटो निवडा.':'Choose a JPG, PNG or WEBP photo up to 15 MB.');
        return;
      }
      const reader = new FileReader();
      reader.onload = (uploadEvt) => {
        setCapturedPages((prev) => [
          ...prev,
          { file, dataUrl: uploadEvt.target.result, pageNumber: prev.length + 1 },
        ]);
        setActivePageIndex(capturedPages.length);
        setAddingPage(false);
        stopCamera();
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFinish = () => {
    if (capturedPages.length === 0) return;
    onCompleteCapture(capturedPages.map(page=>page.file));
  };

  return (
    <div ref={dialogRef} role="dialog" aria-modal="true" aria-label={t.cameraButton} tabIndex={-1} className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-clarity-charcoal/50 backdrop-blur-sm">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-xl w-full p-6 animate-in fade-in zoom-in-95">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-clarity-teal">
            {t.cameraButton}
          </h2>
          <button
            onClick={onClose}
            className="text-clarity-muted hover:text-clarity-charcoal p-1 rounded-full hover:bg-clarity-ivory"
            aria-label={language==='hi'?'कैमरा बंद करें':language==='mr'?'कॅमेरा बंद करा':'Close camera'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {capturedPages.length === 0 || addingPage ? (
          <div>
            <div className="relative aspect-[4/3] bg-black rounded-2xl overflow-hidden mb-4 flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`w-full h-full object-cover ${streamActive ? 'block' : 'hidden'}`}
              />
              {!streamActive && (
                <div className="text-center p-6 text-white">
                  <p className="text-sm mb-4">
                    {permissionError || (language === 'hi' ? 'कैमरा शुरू हो रहा है...' : language === 'mr' ? 'कॅमेरा सुरू होत आहे...' : 'Starting camera...')}
                  </p>
                  <Button
                    size="sm"
                    variant="mint"
                    onClick={() => fileFallbackRef.current?.click()}
                  >
                    {language === 'hi' ? 'गैलरी / फ़ाइल से फ़ोटो चुनें' : language === 'mr' ? 'गॅलरी / फाईलमधून फोटो निवडा' : 'Choose photo from device'}
                  </Button>
                  <input
                    ref={fileFallbackRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden"
                    onChange={handleFallbackFile}
                  />
                </div>
              )}
            </div>

            {streamActive && (
              <div className="flex justify-center">
                <Button size="lg" variant="primary" onClick={handleSnap}>
                  📸 {language === 'hi' ? 'फ़ोटो लें' : language === 'mr' ? 'फोटो काढा' : 'Capture Report'}
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div>
            <div className="aspect-[4/3] bg-clarity-ivory rounded-2xl overflow-hidden mb-4 flex items-center justify-center border border-clarity-border">
              <img
                src={capturedPages[activePageIndex]?.dataUrl}
                alt={language==='hi'?'ली गई फ़ोटो':language==='mr'?'काढलेला फोटो':'Captured document'}
                className="max-h-full object-contain"
              />
            </div>
            <div className="flex flex-wrap gap-2 mb-4">{capturedPages.map((page,index)=><Button key={index} size="sm" variant={index===activePageIndex?'primary':'secondary'} onClick={()=>setActivePageIndex(index)} aria-pressed={index===activePageIndex}>{language==='hi'?'पृष्ठ':language==='mr'?'पान':'Page'} {index+1}</Button>)}</div>
            <p className="mb-4">{language==='hi'?'चुने गए पृष्ठ':language==='mr'?'निवडलेली पाने':'Selected pages'}: {capturedPages.length}</p>
            <div className="flex flex-wrap justify-between gap-3 items-center">
              <Button size="sm" variant="secondary" disabled={capturedPages.length>=10} onClick={()=>{setAddingPage(true);startCamera();}}>{language==='hi'?'अगला पृष्ठ जोड़ें':language==='mr'?'पुढील पान जोडा':'Add another page'}</Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => {
                  setCapturedPages([]);
                  startCamera();
                }}
              >
                {language === 'hi' ? 'दोबारा लें' : language === 'mr' ? 'पुन्हा काढा' : 'Retake'}
              </Button>
              <Button size="md" variant="primary" onClick={handleFinish}>
                {language === 'hi' ? 'इस रिपोर्ट का विश्लेषण करें' : language === 'mr' ? 'या अहवालाचे विश्लेषण करा' : 'Process This Report'} &rarr;
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
