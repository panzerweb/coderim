import java.io.*;
import java.util.*;

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
    static int[] tin, tout, depth;
    static int[][] up;
    static boolean fixed(int u, int v) { return tin[u] <= tin[v] && tin[v] < tout[u]; }
    static boolean ancestor(int root, int u, int v) {
        if (u == v || u == root) return true;
        if (!fixed(u, root)) return fixed(u, v);
        int child = root, distance = depth[root] - depth[u] - 1, bit = 0;
        while (distance > 0) {
            if ((distance & 1) != 0) child = up[bit][child];
            distance >>= 1; bit++;
        }
        return !fixed(child, v);
    }
    @SuppressWarnings("unchecked")
    public static void main(String[] args) throws Exception {
        Input in = new Input(); int n = in.number();
        ArrayList<Integer>[] adjacent = new ArrayList[n];
        for (int i = 0; i < n; i++) adjacent[i] = new ArrayList<>();
        for (int i = 1; i < n; i++) {
            int p = in.number() - 1, c = in.number() - 1;
            adjacent[p].add(c); adjacent[c].add(p);
        }
        int levels = 32 - Integer.numberOfLeadingZeros(n);
        up = new int[levels][n]; depth = new int[n]; tin = new int[n]; tout = new int[n];
        ArrayDeque<int[]> stack = new ArrayDeque<>(); stack.push(new int[]{0, -1, 0});
        int clock = 0;
        while (!stack.isEmpty()) {
            int[] item = stack.pop(); int v = item[0], p = item[1];
            if (item[2] == 1) { tout[v] = clock; continue; }
            up[0][v] = p < 0 ? v : p; tin[v] = clock++;
            stack.push(new int[]{v, p, 1});
            for (int c : adjacent[v]) if (c != p) {
                depth[c] = depth[v] + 1; stack.push(new int[]{c, v, 0});
            }
        }
        for (int k = 1; k < levels; k++) for (int v = 0; v < n; v++) up[k][v] = up[k-1][up[k-1][v]];
        int q = in.number(), root = 0;
        BufferedWriter out = new BufferedWriter(new OutputStreamWriter(System.out));
        while (q-- > 0) {
            if (in.next().equals("ROOT")) root = in.number() - 1;
            else { int u = in.number() - 1, v = in.number() - 1; out.write(ancestor(root, u, v) ? "YES" : "NO"); out.newLine(); }
        }
        out.flush();
    }
}
