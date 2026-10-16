import React, { useState } from 'react';

export function ReportTrends({ history, language = 'en' }) {
  const [selected, setSelected] = useState('');
  const copy = {
    en: ['Your trends', 'Choose a test', 'Upload another comparable report to see a trend. Only matching tests and units are compared.', 'over time', 'Clinical reference interval', 'Previous', 'Current', 'Personal historical average', 'This describes your stored readings. It does not replace the laboratory reference interval.', 'At least four comparable reports are needed for a personal baseline.', 'Upload date', 'Reading'],
    hi: ['आपके रुझान', 'परीक्षण चुनें', 'रुझान के लिए एक और तुलनीय रिपोर्ट जोड़ें। केवल समान परीक्षण और इकाइयों की तुलना होती है।', 'समय के साथ', 'नैदानिक संदर्भ सीमा', 'पिछला', 'वर्तमान', 'व्यक्तिगत ऐतिहासिक औसत', 'यह सहेजे मापों का वर्णन है। प्रयोगशाला संदर्भ सीमा नहीं बदलती।', 'व्यक्तिगत आधार के लिए कम से कम चार तुलनीय रिपोर्ट चाहिए।', 'अपलोड की तारीख', 'माप'],
    mr: ['तुमचे कल', 'चाचणी निवडा', 'कल पाहण्यासाठी आणखी एक तुलनीय अहवाल जोडा. समान चाचण्या आणि एककांचीच तुलना होते.', 'काळानुसार', 'वैद्यकीय संदर्भ मर्यादा', 'मागील', 'सध्याचे', 'वैयक्तिक ऐतिहासिक सरासरी', 'हे जतन केलेल्या मोजमापांचे वर्णन आहे. प्रयोगशाळेची संदर्भ मर्यादा बदलत नाही.', 'वैयक्तिक आधारासाठी किमान चार तुलनीय अहवाल आवश्यक आहेत.', 'अपलोडची तारीख', 'मोजमाप']
  }[language];
  const groups = new Map();
  [...history].reverse().forEach(record => record.measurements?.forEach(item => {
    if (item.requires_verification || !/^\d+(\.\d+)?$/.test(String(item.value))) return;
    const key = `${item.canonical_name || item.name}|${item.unit}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push({ ...item, date: record.date, reportId: record.id });
  }));
  const key = groups.has(selected) ? selected : [...groups.keys()][0];
  const readings = groups.get(key) || [];
  const current = readings.at(-1), previous = readings.at(-2);
  const match = current?.reference_range?.match(/^\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)/);
  const bounds = match ? [Number(match[1]), Number(match[2])] : [];
  const numbers = readings.map(item=>Number(item.value));
  const min = Math.min(...numbers, ...bounds), max = Math.max(...numbers, ...bounds);
  const span = max-min || 1, y = value => 195 - ((value-min)/span)*145;
  const x = index => 45 + index / Math.max(1,readings.length-1)*430;
  return <section className="bg-white rounded-3xl p-6 sm:p-8 border border-clarity-border mt-8">
    <h2 className="text-2xl font-bold mb-4">{copy[0]}</h2>
    {!current ? <p className="text-clarity-muted">{copy[2]}</p> : <>
      <label htmlFor="trend-test" className="block font-semibold mb-2">{copy[1]}</label>
      <select id="trend-test" value={key} onChange={event=>setSelected(event.target.value)} className="w-full p-3 rounded-xl border border-clarity-border mb-6">{[...groups].map(([id,items])=><option key={id} value={id}>{items[0].name} ({items[0].unit})</option>)}</select>
      <h3 className="text-2xl sm:text-3xl font-bold mb-4">{current.name} {copy[3]}</h3>
      {readings.length < 2 ? <p className="text-clarity-muted mb-4">{copy[2]}</p> : <svg viewBox="0 0 520 240" className="w-full" role="img" aria-label={`${current.name}: ${readings.map(item=>`${new Date(item.date).toLocaleDateString(language)} ${item.value} ${item.unit}`).join('; ')}`}>
        {bounds.length===2 && <rect x="30" y={y(bounds[1])} width="460" height={Math.max(1,y(bounds[0])-y(bounds[1]))} fill="#DCF3E2"/>}
        <line x1="30" x2="490" y1="205" y2="205" stroke="#E5E5E8"/>
        <polyline fill="none" stroke="#D24726" strokeWidth="4" points={readings.map((item,i)=>`${x(i)},${y(Number(item.value))}`).join(' ')}/>
        {readings.map((item,i)=><g key={item.reportId}><circle cx={x(i)} cy={y(Number(item.value))} r="5" fill="white" stroke="#D24726" strokeWidth="3"/><text x={x(i)} y="229" textAnchor="middle" fontSize="12" fill="#62626A">{i===0||i===readings.length-1?new Date(item.date).toLocaleDateString(language,{month:'short',day:'numeric'}):''}</text></g>)}
      </svg>}
      <p className="text-sm text-clarity-muted mb-5">{copy[4]}: {current.reference_range || '—'}</p>
      <div className="grid sm:grid-cols-2 gap-4 mb-5">{[[copy[5],previous],[copy[6],current]].map(([label,item])=><div key={label} className="rounded-2xl bg-clarity-ivory p-5"><p className="text-clarity-muted">{label}</p><p className="text-3xl font-bold mt-2 tabular-nums">{item ? `${item.value} ${item.unit}` : '—'}</p></div>)}</div>
      {readings.length >=4 ? <p className="bg-clarity-mint rounded-2xl p-5"><strong>{copy[7]}: {(numbers.reduce((a,b)=>a+b,0)/numbers.length).toFixed(2)} {current.unit}</strong><br/>{copy[8]}</p> : <p className="text-clarity-muted">{copy[9]}</p>}
      <details className="mt-5"><summary className="cursor-pointer font-semibold text-clarity-teal py-3">{copy[10]} · {copy[11]}</summary><table className="w-full text-left"><thead><tr><th>{copy[10]}</th><th>{copy[11]}</th></tr></thead><tbody>{readings.map(item=><tr key={item.reportId}><td className="py-2">{new Date(item.date).toLocaleDateString(language)}</td><td>{item.value} {item.unit}</td></tr>)}</tbody></table></details>
    </>}
  </section>;
}
