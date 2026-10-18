import React from 'react';
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
import { InlineDoctorSection } from '../src/components/journey/InlineDoctorSection';

const provider={id:'place_fixture',name:'Fixture Clinic',specialty:'Doctor business listing',source:'external_discovery',address:'Fixture address',phone_available:true,consultation_options:[{type:'call',url:'tel:+911234567890',evidence:'Maps listing'},{type:'website',url:'https://example.org/clinic',evidence:'Provider website'}],maps_url:'https://www.google.com/maps/search/?api=1&query_place_id=place_fixture'};
function backend(){
  return vi.fn(async(url,options)=>{
    if(url==='/api/v1/consultation/pdf')return {ok:true,status:200,blob:async()=>new Blob(['%PDF test'],{type:'application/pdf'})};
    return {ok:true,status:200,json:async()=>url.includes('/doctors')?{providers:[provider],resolved_location:{display_name:'Test location'},live_provider_api_configured:true,searched_radius_m:10000}:url.includes('history/list')?{reports:[{id:'second_report',filename:'Second report'}]}:{findings:[{name:'Glucose',value:'124.5 mg/dL',reference_range:'70 - 99',status:'high'}],questions:['What should I discuss?'],sharing_status:'not_shared'}};
  });
}
afterEach(()=>{vi.unstubAllGlobals();vi.restoreAllMocks();});

describe('Consultation and explicit report consent',()=>{
  it('shows supported contact only, requires consent, and does not claim a booking',async()=>{
    const fetchMock=backend();vi.stubGlobal('fetch',fetchMock);
    render(<InlineDoctorSection reportId="real_report" isExpanded language="en"/>);
    await screen.findByRole('heading',{name:'Fixture Clinic'});
    fireEvent.click(screen.getByRole('button',{name:'View profile'}));
    const dialog=screen.getByRole('dialog');
    fireEvent.click(within(dialog).getByRole('button',{name:'Consult Doctor'}));
    await within(dialog).findByText('Glucose: 124.5 mg/dL (high); 70 - 99');
    const download=within(dialog).getByRole('button',{name:'Download consultation-ready PDF'});
    expect(download).toBeDisabled();
    expect(within(dialog).getByText(/No appointment has been booked/)).toBeInTheDocument();
    expect(within(dialog).queryByRole('link',{name:'Online Consultation'})).not.toBeInTheDocument();
    expect(within(dialog).queryByRole('link',{name:'WhatsApp Consultation'})).not.toBeInTheDocument();
    expect(within(dialog).getByRole('link',{name:'Call Doctor/Clinic'})).toHaveAttribute('href','tel:+911234567890');
    const checkbox=within(dialog).getByRole('checkbox');fireEvent.click(checkbox);
    expect(download).toBeEnabled();
    URL.createObjectURL=vi.fn(()=>'blob:local-pdf');URL.revokeObjectURL=vi.fn();
    vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});
    fireEvent.click(download);
    await waitFor(()=>expect(fetchMock.mock.calls.some(([url])=>url==='/api/v1/consultation/pdf')).toBe(true));
    const [,request]=fetchMock.mock.calls.find(([url])=>url==='/api/v1/consultation/pdf');
    expect(JSON.parse(request.body)).toEqual({report_id:'real_report',language:'en',consent_to_include_report:true});
    fireEvent.change(within(dialog).getByRole('combobox'),{target:{value:'second_report'}});
    expect(checkbox).not.toBeChecked();
    expect(download).toBeDisabled();
  });
  it.each([['hi','प्रोफ़ाइल देखें','डॉक्टर से परामर्श'],['mr','प्रोफाइल पाहा','डॉक्टरांचा सल्ला घ्या']])('supports consultation consent in %s',async(language,profile,consult)=>{
    vi.stubGlobal('fetch',backend());render(<InlineDoctorSection reportId="real_report" isExpanded language={language}/>);
    await screen.findByRole('heading',{name:'Fixture Clinic'});fireEvent.click(screen.getByRole('button',{name:profile}));
    fireEvent.click(within(screen.getByRole('dialog')).getByRole('button',{name:consult}));
    expect(await screen.findByRole('checkbox')).not.toBeChecked();
  });
});


it('searches Panvel using report specialty and exposes source ratings',async()=>{
  const requests=[];
  vi.stubGlobal('fetch',vi.fn(async(url)=>{
    requests.push(url);
    return {ok:true,status:200,json:async()=>({providers:[{...provider,rating:4.8,user_rating_count:120}],selected_specialty_id:'endocrinology',recommended_specialties:[{specialty_id:'endocrinology',specialty_name:'Endocrinologist',observed_finding:'Glucose finding',why_suggesting:'Discuss the verified result with a clinician.'},{specialty_id:'general_physician',specialty_name:'General Physician'}]})};
  }));
  render(<InlineDoctorSection reportId="real_report" isExpanded language="en"/>);
  await screen.findByText('★ 4.8/5 · 120 reviews');
  expect(screen.getByLabelText('Specialty related to your report')).toHaveValue('endocrinology');
  fireEvent.change(screen.getByLabelText('Enter city or PIN code (e.g., Mumbai, 411004)'),{target:{value:'Panvel'}});
  fireEvent.click(screen.getByRole('button',{name:'Update Location'}));
  await waitFor(()=>expect(requests.some(url=>url.includes('city=Panvel') && url.includes('specialty_id=endocrinology') && url.includes('sort_by=top_rated'))).toBe(true));
  expect(screen.getByText(/Google ratings describe patient reviews/)).toBeInTheDocument();
});
