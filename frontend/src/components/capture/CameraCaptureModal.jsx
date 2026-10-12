import React, { useRef, useState, useEffect, useCallback } from 'react';
import { Button } from '../common/WarmUI';

export function CameraCaptureModal({ isOpen, onClose, onCompleteCapture }) {
  const videoRef = useRef(null);
  const fileFallbackRef = useRef(null);
  const streamRef = useRef(null);

  const [streamActive, setStreamActive] = useState(false);
  const [permissionError, setPermissionError] = useState(null);
  const [capturedPages, setCapturedPages] = useState([]);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [rotation, setRotation] = useState(0);
  const [blurWarning, setBlurWarning] = useState(false);
  const [facingMode, setFacingMode] = useState('environment'); // Prefer rear-facing camera

  // Start Camera Stream cleanly
  const startCamera = useCallback(async () => {
    setPermissionError(null);
    setBlurWarning(false);

    // Stop existing stream if any
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setPermissionError('Live camera is not supported or requires a secure context (HTTPS/localhost). Please use the photo file picker instead.');
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
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermissionError('Camera access was denied. Please allow camera permissions in your browser or choose a photo from your device.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setPermissionError('No camera found on this device. You can still upload report photos below.');
      } else {
        setPermissionError(`Unable to start camera preview: ${err.message || 'Unknown error'}. Please use the file picker.`);
      }
      setStreamActive(false);
    }
  }, [facingMode]);

  // Clean up camera stream on close / unmount
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

  if (!isOpen) return null;

  // Take Snapshot from video canvas
  const handleSnap = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Heuristic light blur/glare check via simple luminance variance estimation
    try {
      const imgData = ctx.getImageData(0, 0, Math.min(100, canvas.width), Math.min(100, canvas.height));
      let sum = 0;
      for (let i = 0; i < imgData.data.length; i += 4) {
        sum += (imgData.data[i] + imgData.data[i + 1] + imgData.data[i + 2]) / 3;
      }
      const avg = sum / (imgData.data.length / 4);
      if (avg < 20 || avg > 240) {
        setBlurWarning(true);
      } else {
        setBlurWarning(false);
      }
    } catch {
      // ignore cross-origin canvas security if any
    }

    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    setCapturedPages((prev) => [...prev, dataUrl]);
    setActivePageIndex(capturedPages.length);
    stopCamera();
  };

  // Native input fallback handling (e.g. mobile native capture)
  const handleNativeCapture = (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      setCapturedPages((prev) => [...prev, event.target.result]);
      setActivePageIndex(capturedPages.length);
      setPermissionError(null);
    };
    reader.readAsDataURL(file);
  };

  // Retake current page
  const handleRetake = (index) => {
    setCapturedPages((prev) => prev.filter((_, i) => i !== index));
    if (capturedPages.length <= 1) {
      startCamera();
    } else {
      setActivePageIndex(Math.max(0, index - 1));
    }
  };

  // Rotate preview
  const handleRotate = () => {
    setRotation((r) => (r + 90) % 360);
  };

  // Convert captured dataUrls to File objects and pass to common pipeline
  const handleConfirmPages = async () => {
    if (capturedPages.length === 0) return;
    stopCamera();
    
    // Convert first captured page (or combined) to File object
    const res = await fetch(capturedPages[0]);
    const blob = await res.blob();
    const file = new File([blob], `captured_report_p1.jpg`, { type: 'image/jpeg' });
    onCompleteCapture(file);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-clarity-charcoal/60 backdrop-blur-sm">
      <div className="bg-clarity-surface rounded-3xl border border-clarity-border shadow-elevated max-w-xl w-full p-4 sm:p-6 flex flex-col max-h-[95vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-clarity-teal">
              Take a photo of your report
            </h2>
            <p className="text-xs text-clarity-muted">
              Position all four corners of the page clearly inside the frame.
            </p>
          </div>
          <button
            onClick={() => { stopCamera(); onClose(); }}
            className="text-clarity-muted hover:text-clarity-charcoal p-1 rounded-full hover:bg-clarity-ivory"
            aria-label="Close camera"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Permission / Unsupported Warning Banner */}
        {permissionError && (
          <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-2xl text-xs sm:text-sm text-[#855B18]">
            <p className="font-semibold mb-2">{permissionError}</p>
            <input
              ref={fileFallbackRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={handleNativeCapture}
            />
            <Button
              size="sm"
              variant="secondary"
              onClick={() => fileFallbackRef.current?.click()}
              className="w-full sm:w-auto"
            >
              Choose photo or use native camera &rarr;
            </Button>
          </div>
        )}

        {/* Glare / Blur Alert */}
        {blurWarning && (
          <div className="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-xl text-xs text-[#9E3624] flex items-center gap-2">
            <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Notice: Document lighting looks very dark or high glare. Consider retaking with steady light.</span>
          </div>
        )}

        {/* Viewport Area */}
        <div className="relative bg-clarity-charcoal rounded-2xl overflow-hidden aspect-[4/3] flex items-center justify-center border border-clarity-border">
          {capturedPages.length === 0 ? (
            <>
              <video
                ref={videoRef}
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              {/* Overlay target frame */}
              <div className="absolute inset-4 border-2 border-white/40 border-dashed rounded-xl pointer-events-none flex items-center justify-center">
                <span className="text-white/60 text-xs px-2 py-1 bg-black/40 rounded-md">
                  Align report edges here
                </span>
              </div>
            </>
          ) : (
            <div className="relative w-full h-full flex items-center justify-center bg-zinc-900 overflow-hidden">
              <img
                src={capturedPages[activePageIndex]}
                alt={`Captured report page ${activePageIndex + 1}`}
                style={{ transform: `rotate(${rotation}deg)` }}
                className="max-h-full max-w-full object-contain transition-transform duration-200"
              />
              <div className="absolute bottom-2 left-2 bg-black/60 text-white text-xs px-2.5 py-1 rounded-full">
                Page {activePageIndex + 1} of {capturedPages.length}
              </div>
            </div>
          )}
        </div>

        {/* Multi-page Thumbnail strip */}
        {capturedPages.length > 0 && (
          <div className="flex items-center gap-2 mt-3 overflow-x-auto pb-1">
            {capturedPages.map((page, idx) => (
              <button
                key={idx}
                onClick={() => setActivePageIndex(idx)}
                className={`w-14 h-14 rounded-lg overflow-hidden border-2 shrink-0 ${
                  activePageIndex === idx ? 'border-clarity-teal ring-2 ring-clarity-mint' : 'border-clarity-border opacity-70'
                }`}
              >
                <img src={page} alt="" className="w-full h-full object-cover" />
              </button>
            ))}
            <button
              onClick={() => {
                startCamera();
              }}
              className="w-14 h-14 rounded-lg border-2 border-dashed border-clarity-border hover:border-clarity-teal flex flex-col items-center justify-center text-clarity-teal shrink-0 text-xs font-semibold"
              title="Add another page"
            >
              <span>+ Add</span>
              <span>Page</span>
            </button>
          </div>
        )}

        {/* Action Controls */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-clarity-border">
          {capturedPages.length === 0 ? (
            <>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setFacingMode((m) => (m === 'user' ? 'environment' : 'user'))}
                  title="Switch camera"
                >
                  Flip Camera
                </Button>
                <input
                  ref={fileFallbackRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="hidden"
                  onChange={handleNativeCapture}
                />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => fileFallbackRef.current?.click()}
                >
                  Choose file
                </Button>
              </div>

              <Button
                variant="coral"
                onClick={handleSnap}
                className="px-6 py-3"
                disabled={!streamActive}
              >
                Snap Photo
              </Button>
            </>
          ) : (
            <>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={handleRotate}
                  title="Rotate image 90 degrees"
                >
                  Rotate
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleRetake(activePageIndex)}
                  className="text-red-700"
                >
                  Retake page
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="primary"
                  onClick={handleConfirmPages}
                >
                  Continue with {capturedPages.length} {capturedPages.length === 1 ? 'page' : 'pages'} &rarr;
                </Button>
              </div>
            </>
          )}
        </div>

      </div>
    </div>
  );
}
