// Immutable verifier source. The worker supplies this file; learners cannot select it.
#include <cstddef>
#include <exception>
#include <fstream>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

int ds60_learner_main();
namespace ds60 {
long long positive_sum(const std::vector<int>&);
bool replace_at(std::vector<int>&, std::size_t, int);
std::optional<int> checked_read(const std::vector<int>&, long long);
std::vector<int> nonnegative_copy(const std::vector<int>&);
}
struct Check { const char* name; bool passed; const char* detail; };
int main() {
    std::vector<Check> checks;
    const auto add = [&checks](const char* name, bool ok, const char* detail) {
        checks.push_back({name,ok,detail});
    };
    try {
        if (ds60_learner_main() != 0) {
            add("learner-main",false,"Worked-example entry point returned nonzero");
        } else {
            const std::vector<int> mixed{4,-2,7,0,9};
            const auto before=mixed;
            add("mixed-sum-input",ds60::positive_sum(mixed)==20 && mixed==before,"Mixed sum20; immutable input");
            add("empty-sum",ds60::positive_sum({})==0,"Empty sum0");
            add("negative-sum",ds60::positive_sum({-4,-1})==0,"Negative-only sum0");
            add("wide-accumulator",ds60::positive_sum(std::vector<int>(10000,1000000))==10000000000LL,"Wide exact sum10000000000");
            std::vector<int> values{4,7,9};
            add("valid-replacement",ds60::replace_at(values,1,8) && values==std::vector<int>({4,8,9}),"Index1 changes one value");
            const auto saved=values;
            add("one-past-replacement",!ds60::replace_at(values,3,8) && values==saved,"One-past rejected without mutation");
            std::vector<int> empty;
            add("empty-replacement",!ds60::replace_at(empty,0,8) && empty.empty(),"Empty rejected without mutation");
            const std::vector<int> readings{4,7,9};
            add("valid-read",ds60::checked_read(readings,1)==std::optional<int>(7),"Valid optional7");
            add("negative-read",!ds60::checked_read(readings,-1).has_value(),"Negative index rejected");
            add("one-past-read",!ds60::checked_read(readings,3).has_value(),"One-past rejected");
            add("empty-read",!ds60::checked_read({},0).has_value(),"Empty read rejected");
            const std::vector<int> temperatures{3,-1,0,5};
            auto filtered=ds60::nonnegative_copy(temperatures);
            const bool correct=filtered==std::vector<int>({3,0,5}) && temperatures==std::vector<int>({3,-1,0,5});
            if(!filtered.empty()) filtered.at(0)=99;
            add("filter-ownership",correct && temperatures.at(0)==3,"Filter preserves order,zero and independent ownership");
            add("empty-filter",ds60::nonnegative_copy({}).empty(),"Empty filter result");
            add("negative-filter",ds60::nonnegative_copy({-3,-1}).empty(),"All-negative filter empty");
        }
    } catch(const std::exception&) {
        add("unexpected-exception",false,"Learner helper raised before its contract completed");
    } catch(...) {
        add("unexpected-exception",false,"Learner helper raised a nonstandard exception");
    }
    std::ofstream out("checks.json",std::ios::trunc);
    if(!out) return 2;
    out << "{\"checks\":[";
    bool all=!checks.empty();
    for(std::size_t i=0;i<checks.size();++i) {
        if(i) out << ',';
        const auto& c=checks.at(i);
        out << "{\"name\":\"" << c.name << "\",\"passed\":" << (c.passed?"true":"false")
            << ",\"detail\":\"" << c.detail << "\"}";
        all=all&&c.passed;
    }
    out << "]}\n";
    out.close();
    if(!out) return 2;
    std::cout << checks.size() << " checks recorded\n";
    return all ? 0 : 1;
}
