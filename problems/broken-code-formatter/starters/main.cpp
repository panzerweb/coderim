#include <iostream>
#include <string>

int main() {
    std::string source;
    std::getline(std::cin, source);
    if (!source.empty() && source.back() == '\r') source.pop_back();
    // Preserve spaces. Print VALID or INVALID.
    return 0;
}
