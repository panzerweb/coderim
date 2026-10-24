import java.io.*;

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
        int n = in.number();
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
