import React from 'react';
import { vi, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProviderMap } from '../src/components/journey/ProviderMap';
const state = vi.hoisted(()=>({maps:[],markers:[],fail:false}));
vi.mock('maplibre-gl',()=>({
  setWorkerUrl:vi.fn(),NavigationControl:class {},
  LngLatBounds:class {extend(){return this;}},
  Map:class {
    constructor(options){if(state.fail)throw new Error('No WebGL');this.options=options;this.events={};this.remove=vi.fn();this.easeTo=vi.fn();state.maps.push(this);}
    addControl(){} fitBounds(){} on(event,fn){this.events[event]=fn;}
  },
  Marker:class {
    constructor({element}){this.element=element;this.remove=vi.fn();state.markers.push(this);}
    setLngLat(point){this.point=point;return this;} addTo(map){map.options.container.append(this.element);return this;}
  },
}));
const providers=[{id:'osm:node/1',name:'OSM fixture clinic',coordinates:{lat:19.01,lng:73.01}}];
const location={coordinates:{lat:19,lng:73}};
beforeEach(()=>{state.maps=[];state.markers=[];state.fail=false;});
afterEach(()=>vi.restoreAllMocks());
it('connects accessible map markers to provider selection and removes map resources',async()=>{
 const select=vi.fn();const view=render(<ProviderMap providers={providers} location={location} onSelect={select}/>);
 const marker=await screen.findByRole('button',{name:'Select facility: OSM fixture clinic'});
 fireEvent.click(marker);expect(select).toHaveBeenCalledWith(providers[0]);
 view.rerender(<ProviderMap providers={providers} location={location} onSelect={select} selectedId="osm:node/1"/>);
 expect(marker).toHaveAttribute('aria-pressed','true');
 expect(state.maps[0].easeTo).toHaveBeenCalled();
 expect(state.maps[0].options.style).toBe('https://tiles.openfreemap.org/styles/liberty');
 view.unmount();expect(state.maps[0].remove).toHaveBeenCalled();expect(state.markers[0].remove).toHaveBeenCalled();
});
it('offers a list fallback if WebGL is unavailable',async()=>{
 state.fail=true;render(<ProviderMap providers={providers} location={location} onSelect={()=>{}}/>);
 await waitFor(()=>expect(screen.getByRole('status')).toHaveTextContent('Map unavailable'));
});
it.each([['hi','मानचित्र उपलब्ध नहीं'],['mr','नकाशा उपलब्ध नाही']])('localizes map failure in %s',async(language,text)=>{
 state.fail=true;render(<ProviderMap providers={providers} location={location} language={language} onSelect={()=>{}}/>);
 await waitFor(()=>expect(screen.getByRole('status')).toHaveTextContent(text));
});
