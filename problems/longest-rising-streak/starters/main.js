const raw=require('fs').readFileSync(0,'utf8');
const words=raw.trim().split(/\s+/);let position=0;
const token=()=>words[position++],number=()=>Number(token());
const t=number();
for(let test=0;test<t;test++){const n=number(), temperatures=Array.from({length:n},number);
  // TODO: print one answer for this test case.
}
// TODO: solve the problem and print only the required answer(s).
