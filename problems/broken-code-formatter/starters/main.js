const fs = require('fs');
const source = fs.readFileSync(0, 'utf8').replace(/\r?\n$/, '');

// Read one source-code line, preserving spaces. Print VALID or INVALID.
