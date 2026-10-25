// YOUR SOLUTION: edit this function body.
function isNumber(s) {
  // TODO: implement the function.
  return false;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const s=raw.replace(/\r?\n$/, '');
const result=isNumber(s);
process.stdout.write(JSON.stringify(result)+'\n');
