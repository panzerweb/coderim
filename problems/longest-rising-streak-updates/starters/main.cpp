#include <iostream>
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
