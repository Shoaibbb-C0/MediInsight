import React from 'react';
import {it,expect,vi,afterEach} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {VerificationScreen} from '../src/components/verification/VerificationScreen';
import {apiFetch} from '../src/api';

afterEach(()=>{vi.unstubAllGlobals();vi.restoreAllMocks();});

it('does not mark a reading saved when verification is rejected',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>({ok:false,status:503})));
 const next=vi.fn();
 render(<VerificationScreen reportId="real" biomarkers={[{id:'b',name:'Test source',value:'0.9',unit:'mg/dL',reference_range:'',requires_verification:true}]} onConfirmAll={next} onBack={()=>{}}/>);
 fireEvent.click(screen.getByRole('button',{name:'Save reading'}));
 expect(await screen.findByRole('alert')).toHaveTextContent('not saved');
 fireEvent.click(screen.getByRole('button',{name:'Continue to questions'}));
 expect(next.mock.calls[0][0][0].requires_verification).toBe(true);
});

it('deduplicates concurrent session refresh and retries only after success',async()=>{
 const seen=new Map();
 const fetchMock=vi.fn(async(url)=>{
  if(url.includes('/auth/refresh'))return {ok:true,status:200};
  const count=seen.get(url)||0;seen.set(url,count+1);
  return {ok:count>0,status:count>0?200:401};
 });vi.stubGlobal('fetch',fetchMock);
 const results=await Promise.all([apiFetch('/api/v1/reports/a/summary'),apiFetch('/api/v1/reports/b/summary')]);
 expect(results.every(item=>item.status===200)).toBe(true);
 expect(fetchMock.mock.calls.filter(([url])=>url.includes('/auth/refresh'))).toHaveLength(1);
});

it('expires patient UI when retry still rejects the session',async()=>{
 const expired=vi.fn();window.addEventListener('simplifier-session-expired',expired);
 vi.stubGlobal('fetch',vi.fn(async(url)=>({ok:url.includes('/auth/refresh'),status:url.includes('/auth/refresh')?200:401})));
 try{await apiFetch('/api/v1/reports/a/summary');expect(expired).toHaveBeenCalledTimes(1);}
 finally{window.removeEventListener('simplifier-session-expired',expired);}
});
