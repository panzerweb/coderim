#include <iostream>
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
