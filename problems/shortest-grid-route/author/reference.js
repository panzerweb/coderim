// Private organizer reference. Tokenized input and buffered output count toward total space.
const raw = require('fs').readFileSync(0, 'utf8');
let position = 0; const words = raw.trim().split(/\s+/);
const token = () => words[position++], number = () => Number(token());
const answers = [];
const rows = number(), cols = number(), grid = [];
let start = -1;
for (let r = 0; r < rows; r++) {
  grid.push(token()); const c = grid[r].indexOf('S'); if (c >= 0) start = r * cols + c;
}
const dist = new Int32Array(rows * cols).fill(-1), queue = [start];
dist[start] = 0; let result = -1;
for (let head = 0; head < queue.length; head++) {
  const cell = queue[head], r = Math.floor(cell / cols), c = cell % cols;
  if (grid[r][c] === 'E') { result = dist[cell]; break; }
  for (const [nr,nc] of [[r-1,c],[r+1,c],[r,c-1],[r,c+1]]) {
    if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
      const next = nr * cols + nc;
      if (grid[nr][nc] !== '#' && dist[next] < 0) { dist[next] = dist[cell] + 1; queue.push(next); }
    }
  }
}
console.log(result);
