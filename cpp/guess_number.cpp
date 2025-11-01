#include <iostream>
#include <cstdlib>
#include <ctime>

int main() {
    std::srand(static_cast<unsigned int>(std::time(nullptr)));
    int secret = std::rand() % 10 + 1; // random number between 1 and 10

    int guess = 0;
    std::cout << "Guess a number between 1 and 10: ";
    std::cin >> guess;

    if (guess == secret) {
        std::cout << "You guessed correctly!" << std::endl;
    } else {
        std::cout << "Sorry, the number was " << secret << std::endl;
    }

    return 0;
}
