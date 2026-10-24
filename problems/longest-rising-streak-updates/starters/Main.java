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
        int testCases = in.number();
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
