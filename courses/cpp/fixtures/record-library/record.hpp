#ifndef DS60_RECORD_HPP
#define DS60_RECORD_HPP
#include <optional>
#include <string_view>
namespace ds60_records {
struct Record {
  int id;
  int cents;
};
std::optional<Record> parse_record(std::string_view text);
} // namespace ds60_records
#endif
