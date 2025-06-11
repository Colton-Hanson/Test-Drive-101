#include <iostream>

int main() {
    int a = 0;
    int b = 0;

    std::cout << "Enter first number: ";
    std::cin >> a;

    std::cout << "Enter second number: ";
    std::cin >> b;

    int sum = a + b;
    std::cout << "Sum: " << sum << std::endl;

    return 0;
}
