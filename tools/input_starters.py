"""Fast input scaffolds only; no challenge algorithm is included."""
from pathlib import Path


JAVA_INPUT = '''import java.io.*;

public class Main {
    static class FastInput {
        private final InputStream in = new BufferedInputStream(System.in);
        String next() throws IOException {
            int c;
            do { c = in.read(); } while (c >= 0 && c <= 32);
            StringBuilder token = new StringBuilder();
            while (c > 32) { token.append((char)c); c = in.read(); }
            return token.toString();
        }
        int number() throws IOException { return Integer.parseInt(next()); }
    }
    public static void main(String[] args) throws Exception {
        FastInput in = new FastInput();
'''

JS_INPUT = '''const fs = require('fs');
const input = fs.readFileSync(0, 'utf8');
let cursor = 0;
function next() {
  while (cursor < input.length && input.charCodeAt(cursor) <= 32) cursor++;
  const start = cursor;
  while (cursor < input.length && input.charCodeAt(cursor) > 32) cursor++;
  return input.slice(start, cursor);
}
'''


def write_starters(root: Path, streak: bool):
    if streak:
        python = '''import sys

data = (token for line in sys.stdin.buffer for token in line.split())
test_cases = int(next(data))
for _ in range(test_cases):
    n, q = int(next(data)), int(next(data))
    temperatures = [int(next(data)) for _ in range(n)]
    # TODO: prepare your data structure for this test case.
    for _ in range(q):
        command = next(data).decode()
        a, b = int(next(data)), int(next(data))
        # TODO: UPDATE a b, or print the answer for QUERY a b.
'''
        javascript = JS_INPUT + '''const testCases = Number(next());
for (let t = 0; t < testCases; t++) {
  const n = Number(next()), q = Number(next());
  const temperatures = Array.from({length: n}, () => Number(next()));
  // TODO: prepare your data structure for this test case.
  for (let i = 0; i < q; i++) {
    const command = next(), a = Number(next()), b = Number(next());
    // TODO: UPDATE a b, or print the answer for QUERY a b.
  }
}
'''
        java = JAVA_INPUT + '''        int testCases = in.number();
        while (testCases-- > 0) {
            int n = in.number(), q = in.number();
            int[] temperatures = new int[n];
            for (int i = 0; i < n; i++) temperatures[i] = in.number();
            // TODO: prepare your data structure for this test case.
            for (int i = 0; i < q; i++) {
                String command = in.next(); int a = in.number(), b = in.number();
                // TODO: UPDATE a b, or print the answer for QUERY a b.
            }
        }
    }
}
'''
        cpp = '''#include <iostream>
#include <string>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    int t; std::cin >> t;
    while (t--) {
        int n, q; std::cin >> n >> q;
        std::vector<int> temperatures(n);
        for (int &x : temperatures) std::cin >> x;
        // TODO: prepare your data structure for this test case.
        while (q--) {
            std::string command; int a, b; std::cin >> command >> a >> b;
            // TODO: UPDATE a b, or print the answer for QUERY a b.
        }
    }
}
'''
    else:
        python = '''import sys

data = (token for line in sys.stdin.buffer for token in line.split())
n = int(next(data))
edges = [(int(next(data)), int(next(data))) for _ in range(n - 1)]
# TODO: prepare your data structure for the tree initially rooted at 1.
q = int(next(data))
for _ in range(q):
    command = next(data).decode()
    if command == 'ROOT':
        root = int(next(data))
        # TODO: change the logical root.
    else:
        u, v = int(next(data)), int(next(data))
        # TODO: print YES or NO for QUERY u v.
'''
        javascript = JS_INPUT + '''const n = Number(next());
const edges = Array.from({length: n - 1}, () => [Number(next()), Number(next())]);
// TODO: prepare your data structure for the tree initially rooted at 1.
const q = Number(next());
for (let i = 0; i < q; i++) {
  const command = next();
  if (command === 'ROOT') {
    const root = Number(next());
    // TODO: change the logical root.
  } else {
    const u = Number(next()), v = Number(next());
    // TODO: print YES or NO for QUERY u v.
  }
}
'''
        java = JAVA_INPUT + '''        int n = in.number();
        int[][] edges = new int[n - 1][2];
        for (int i = 0; i < n - 1; i++) { edges[i][0] = in.number(); edges[i][1] = in.number(); }
        // TODO: prepare your data structure for the tree initially rooted at 1.
        int q = in.number();
        while (q-- > 0) {
            String command = in.next();
            if (command.equals("ROOT")) {
                int root = in.number();
                // TODO: change the logical root.
            } else {
                int u = in.number(), v = in.number();
                // TODO: print YES or NO for QUERY u v.
            }
        }
    }
}
'''
        cpp = '''#include <iostream>
#include <string>
#include <utility>
#include <vector>
int main() {
    std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
    int n; std::cin >> n;
    std::vector<std::pair<int,int>> edges(n - 1);
    for (auto &edge : edges) std::cin >> edge.first >> edge.second;
    // TODO: prepare your data structure for the tree initially rooted at 1.
    int q; std::cin >> q;
    while (q--) {
        std::string command; std::cin >> command;
        if (command == "ROOT") {
            int root; std::cin >> root;
            // TODO: change the logical root.
        } else {
            int u, v; std::cin >> u >> v;
            // TODO: print YES or NO for QUERY u v.
        }
    }
}
'''
    destination = root / 'starters'
    destination.mkdir(exist_ok=True)
    for name, code in [('main.py', python), ('main.js', javascript), ('main.cpp', cpp), ('Main.java', java)]:
        (destination / name).write_text(code, encoding='utf-8', newline='\n')
