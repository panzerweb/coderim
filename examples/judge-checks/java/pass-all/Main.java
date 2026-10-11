import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public class Main {
    static boolean isValid(String source) {
        char[] stack = new char[source.length()];
        int size = 0;
        char quote = '\0';
        boolean escaped = false;

        for (int i = 0; i < source.length(); i++) {
            char c = source.charAt(i);

            if (quote != '\0') {
                if (escaped) escaped = false;
                else if (c == '\\') escaped = true;
                else if (c == quote) quote = '\0';
            } else if (c == '"' || c == '\'') {
                quote = c;
            } else if (c == '(' || c == '[' || c == '{') {
                stack[size++] = c;
            } else if (c == ')' || c == ']' || c == '}') {
                char expected = c == ')' ? '(' : c == ']' ? '[' : '{';
                if (size == 0 || stack[--size] != expected) return false;
            }
        }

        return size == 0 && quote == '\0' && !escaped;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(System.in, StandardCharsets.UTF_8));
        String source = reader.readLine();
        System.out.println(isValid(source == null ? "" : source) ? "VALID" : "INVALID");
    }
}
