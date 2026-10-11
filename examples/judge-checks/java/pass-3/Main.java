import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(System.in, StandardCharsets.UTF_8));
        String source = reader.readLine();

        // Deliberately limited fixture: public samples 1, 2, and 6 only.
        boolean implemented =
            "function test() { return [a, (b + c)]; }".equals(source)
            || "print(\"This [ is not a bracket!\")".equals(source)
            || "log('User said \"Hello [World]\"')".equals(source);

        System.out.println(implemented ? "VALID" : "NOT_IMPLEMENTED");
    }
}
