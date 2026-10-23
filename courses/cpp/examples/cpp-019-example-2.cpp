#include <algorithm>
#include <cassert>
#include <iostream>
#include <ranges>
#include <vector>

struct Score  {
     int id;
     int points;
};
int main() {
    std::vector<Score> scores{{1,9},{2,4}};
    std::ranges::sort(scores,{},&Score::points);
    assert(scores[0].id==2 && scores[1].id==1);
    std::cout << "cpp-019 example 2 checks passed\n";
    return 0;
}
