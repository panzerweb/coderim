import java.io.*;

public class Main {
    static class Input {
        final InputStream in = System.in;
        final byte[] buffer = new byte[65536];
        int position, length;
        int read() throws IOException {
            if (position == length) { length = in.read(buffer); position = 0; }
            return length < 0 ? -1 : buffer[position++];
        }
        String next() throws IOException {
            int c; do { c = read(); } while (c >= 0 && c <= 32);
            StringBuilder s = new StringBuilder();
            while (c > 32) { s.append((char)c); c = read(); }
            return s.toString();
        }
        int number() throws IOException { return Integer.parseInt(next()); }
    }
    static class Node {
        int length, first, last, prefix, suffix, best;
        Node(int x) { length = prefix = suffix = best = 1; first = last = x; }
        Node(Node a, Node b) {
            boolean joins = a.last < b.first;
            length = a.length + b.length; first = a.first; last = b.last;
            prefix = joins && a.prefix == a.length ? a.length + b.prefix : a.prefix;
            suffix = joins && b.suffix == b.length ? b.length + a.suffix : b.suffix;
            best = Math.max(Math.max(a.best, b.best), joins ? a.suffix + b.prefix : 0);
        }
    }
    static Node merge(Node a, Node b) { return a == null ? b : b == null ? a : new Node(a, b); }
    public static void main(String[] args) throws Exception {
        Input in = new Input();
        BufferedWriter out = new BufferedWriter(new OutputStreamWriter(System.out));
        int t = in.number();
        while (t-- > 0) {
            int n = in.number(), q = in.number(), size = 1;
            while (size < n) size *= 2;
            Node[] tree = new Node[2 * size];
            for (int i = 0; i < n; i++) tree[size + i] = new Node(in.number());
            for (int i = size - 1; i > 0; i--) tree[i] = merge(tree[2*i], tree[2*i+1]);
            while (q-- > 0) {
                String op = in.next(); int a = in.number(), b = in.number();
                if (op.equals("UPDATE")) {
                    int p = size + a - 1; tree[p] = new Node(b);
                    for (p /= 2; p > 0; p /= 2) tree[p] = merge(tree[2*p], tree[2*p+1]);
                } else {
                    int l = size + a - 1, r = size + b;
                    Node before = null, after = null;
                    while (l < r) {
                        if ((l & 1) != 0) before = merge(before, tree[l++]);
                        if ((r & 1) != 0) after = merge(tree[--r], after);
                        l /= 2; r /= 2;
                    }
                    out.write(Integer.toString(merge(before, after).best)); out.newLine();
                }
            }
        }
        out.flush();
    }
}
