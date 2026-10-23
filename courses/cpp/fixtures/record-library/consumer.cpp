#include "record.hpp"
#include <iostream>
#include <string_view>
int main() {
    int accepted=0,rejected=0;
    for(std::string_view row:{"7,125","0,0","7,125x","7,-1"}) {
        if(ds60_records::parse_record(row)) ++accepted;
        else ++rejected;
    }
    if(accepted!=2 || rejected!=2) return 1;
    const auto record=ds60_records::parse_record("7,125");
    if(!record || record->id!=7 || record->cents!=125) return 2;
    std::cout << "accepted=2 rejected=2\n";
    return 0;
}
