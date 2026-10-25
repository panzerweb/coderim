const raw=require('fs').readFileSync(0,'utf8');
const words=raw.trim().split(/\s+/);let position=0;
const token=()=>words[position++],number=()=>Number(token());
const a=number(), b=number();
// TODO: solve the problem and print only the required answer(s).
