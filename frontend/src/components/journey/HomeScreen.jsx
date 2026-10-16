import React from 'react';
import { FileUp, Camera, FileText, ArrowRight } from 'lucide-react';
import { Button } from '../common/WarmUI';
import { TRANSLATIONS } from '../../fixtures/translations';

export function HomeScreen({ onStartUpload, onStartCamera, onViewSample, language = 'en' }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;
  const copy = {
    en: ['UPLOAD', 'Add your report', "Upload a PDF or take a photo. We’ll help explain what matters.", 'Your next step starts with understanding.', 'Drop PDF or photo', 'Choose a report to get started', 'PDF, JPG or PNG · up to 15 MB', 'A clearer picture of your results', 'Your measurements stay connected to their source. We explain the results, then help you explore food guidance and care.', 'Read your results', 'Understand high, low and within-range measurements.', 'Choose your next step', 'Explore nutrition and doctor guidance from your report.', 'Example report · demo data'],
    hi: ['अपलोड', 'अपनी रिपोर्ट जोड़ें', 'PDF अपलोड करें या फ़ोटो लें। हम ज़रूरी बातें समझने में मदद करेंगे।', 'समझने से शुरू होता है अगला कदम।', 'PDF या फ़ोटो चुनें', 'शुरू करने के लिए रिपोर्ट चुनें', 'PDF, JPG या PNG · अधिकतम 15 MB', 'अपने नतीजों को बेहतर समझें', 'माप उनके स्रोत से जुड़े रहते हैं। नतीजे समझें, फिर आहार और डॉक्टर के विकल्प देखें।', 'नतीजे समझें', 'कम, अधिक और सीमा में आए माप समझें।', 'अगला कदम चुनें', 'रिपोर्ट से संबंधित आहार और डॉक्टर मार्गदर्शन देखें।', 'उदाहरण रिपोर्ट · डेमो डेटा'],
    mr: ['अपलोड', 'तुमचा अहवाल जोडा', 'PDF अपलोड करा किंवा फोटो घ्या. महत्त्वाच्या गोष्टी समजून घ्या.', 'पुढचे पाऊल समजून घेण्यापासून सुरू होते.', 'PDF किंवा फोटो निवडा', 'सुरुवातीसाठी अहवाल निवडा', 'PDF, JPG किंवा PNG · कमाल 15 MB', 'तुमचे निकाल नीट समजून घ्या', 'मोजमाप त्यांच्या स्रोताशी जोडलेले राहतात. निकाल समजून आहार आणि डॉक्टरांचे पर्याय पाहा.', 'निकाल समजून घ्या', 'कमी, जास्त आणि मर्यादेतील मोजमाप समजून घ्या.', 'पुढचे पाऊल निवडा', 'अहवालाशी संबंधित आहार आणि डॉक्टरांचे मार्गदर्शन पाहा.', 'उदाहरण अहवाल · डेमो डेटा']
  }[language] || [];
  return <div className="max-w-6xl mx-auto px-5 sm:px-8 py-10 sm:py-16">
    <div className="grid lg:grid-cols-[1fr_1fr] gap-10 lg:gap-20 items-center">
      <section>
        <p className="text-clarity-teal text-sm font-bold tracking-widest mb-4">{copy[0]}</p>
        <h1 className="mb-5 max-w-lg">{copy[1]}</h1>
        <p className="text-lg text-clarity-muted max-w-lg leading-relaxed mb-8">{copy[2]}</p>
        <div className="hidden lg:block border-t border-clarity-border pt-8 mt-12 max-w-md">
          <FileText className="text-clarity-teal w-8 h-8 mb-4" aria-hidden="true" />
          <h2 className="text-2xl font-bold mb-3">{copy[3]}</h2>
          <p className="text-clarity-muted leading-relaxed">{copy[9]}</p>
        </div>
      </section>
      <section className="space-y-4" aria-label={t.uploadButton}>
        <button onClick={onStartUpload} className="w-full border-2 border-dashed border-clarity-teal bg-clarity-mint rounded-3xl px-6 py-12 sm:py-16 flex flex-col items-center text-center hover:bg-white transition-colors">
          <FileUp className="w-12 h-12 text-clarity-teal mb-5" aria-hidden="true" />
          <span className="font-bold text-2xl mb-2">{copy[4]}</span>
          <span className="text-clarity-muted">{copy[5]}</span>
          <span className="text-clarity-muted text-sm mt-5">{copy[6]}</span>
        </button>
        <Button onClick={onStartUpload} className="w-full" size="lg" icon={<FileUp size={20} aria-hidden="true" />}>{t.uploadButton}</Button>
        <Button onClick={onStartCamera} className="w-full" size="lg" variant="secondary" icon={<Camera size={20} aria-hidden="true" />}>{t.cameraButton}</Button>
        <button onClick={onViewSample} className="w-full text-clarity-muted text-sm flex items-center justify-center gap-2 py-3 underline underline-offset-4">{copy[14]}<ArrowRight size={16} aria-hidden="true" /></button>
      </section>
    </div>
    <section className="grid sm:grid-cols-2 gap-5 mt-12 sm:mt-20 border-t border-clarity-border pt-8">
      {[10,12].map((n,i)=><div key={n} className="bg-white rounded-3xl p-6 sm:p-8"><span className="text-clarity-teal font-bold text-sm">0{i+1}</span><h2 className="font-bold text-xl mt-3 mb-2">{copy[n]}</h2><p className="text-clarity-muted leading-relaxed">{copy[n+1]}</p></div>)}
    </section>
  </div>;
}
