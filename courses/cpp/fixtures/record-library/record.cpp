#include "record.hpp"
#include <charconv>
namespace ds60_records {
std::optional<Record> parse_record(std::string_view text) {
    const auto comma=text.find(',');
    if(comma==text.npos) return {};
    int id=0,cents=0;
    const auto [p,e]=std::from_chars(text.data(),text.data()+comma,id);
    const auto [q,f]=std::from_chars(text.data()+comma+1,text.data()+text.size(),cents);
    if(e!=std::errc{} || f!=std::errc{} || p!=text.data()+comma
       || q!=text.data()+text.size() || id<0 || cents<0) return {};
    return Record{id,cents};
}
}
