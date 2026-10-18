import {readFileSync} from 'node:fs';
if(process.env.VERCEL){
 const config=JSON.parse(readFileSync(new URL('../vercel.json',import.meta.url),'utf8'));
 const route=config.rewrites?.find(item=>item.source.startsWith('/api/'));
 if(!route?.destination?.startsWith('https://'))throw new Error('Configure and verify your real backend before hosting: npm.cmd run configure:hosting -- --backend-url https://YOUR-ACTUAL-BACKEND');
}
