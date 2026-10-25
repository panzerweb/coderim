const raw=require('fs').readFileSync(0,'utf8');
const words=raw.trim().split(/\s+/);let position=0;
const token=()=>words[position++],number=()=>Number(token());
const n=number(), edges=[];
for(let i=1;i<n;i++)edges.push([number(),number()]);
const q=number();
for(let i=0;i<q;i++){const u=number(),v=number();
  // TODO: print YES or NO.
}
// TODO: solve the problem and print only the required answer(s).
