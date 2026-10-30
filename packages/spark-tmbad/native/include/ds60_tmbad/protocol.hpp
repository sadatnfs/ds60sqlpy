// SPDX-License-Identifier: MIT
#pragma once
#include "registry.hpp"
#include <json.hpp>
#include <openssl/evp.h>
#include <array>
#include <charconv>
#include <cstdint>
#include <iomanip>
#include <set>
#include <sstream>

#ifndef DS60_NATIVE_BUILD_ID
#error Build preparation must supply a source/dependency/flags-bound DS60_NATIVE_BUILD_ID.
#endif
namespace ds60_tmbad {
using Json = nlohmann::json;
constexpr std::size_t frame_limit = 4 * 1024 * 1024;
inline std::string sha256(const std::string &value) {
  unsigned char digest[EVP_MAX_MD_SIZE];
  unsigned int size = 0;
  require(EVP_Digest(value.data(), value.size(), digest, &size, EVP_sha256(),
                     nullptr) == 1 &&
              size == 32,
          "Digest calculation failed", "INTERNAL_ERROR");
  static const char hex[] = "0123456789abcdef";
  std::string result;
  result.reserve(64);
  for (unsigned i = 0; i < size; ++i) {
    result.push_back(hex[digest[i] >> 4]);
    result.push_back(hex[digest[i] & 15]);
  }
  return result;
}
inline bool hex_digest(const std::string &value) {
  return value.size() == 64 &&
         std::all_of(value.begin(), value.end(), [](unsigned char c) {
           return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
         });
}
inline std::string build_id() {
  const std::string value = DS60_NATIVE_BUILD_ID;
  require(hex_digest(value), "Prepared build identity is invalid",
          "PREPARATION_ERROR");
  return value;
}
inline Json engine_identity() {
  return {{"name", "TMBad"},
          {"version", "1.9.25"},
          {"source_sha256",
           "cf9663b29949cd5eaccb32e11900c9e07caec7d6ac4f17cfd938317dc33acff2"}};
}
inline Json target_json(const Target &target) {
  return {{"fields", target.fields},
          {"columns", target.columns},
          {"needs_history", target.needs_history},
          {"conditioning", target.conditioning},
          {"uncertainty", target.uncertainty}};
}
inline Json descriptor_json(const Descriptor &d) {
  Json bounds = Json::array(), prediction = Json::object(),
       forecast = Json::object();
  for (const auto &bound : d.parameter_bounds)
    bounds.push_back(Json::array(
        {std::isfinite(bound.first) ? Json(bound.first) : Json(nullptr),
         std::isfinite(bound.second) ? Json(bound.second) : Json(nullptr)}));
  for (const auto &t : d.predict)
    prediction[t.name] = target_json(t);
  for (const auto &t : d.forecast)
    forecast[t.name] = target_json(t);
  Json value{{"id", d.id},
             {"version", d.version},
             {"fit_kind", d.fit_kind},
             {"fit_fields", d.fit_fields},
             {"parameter_names", d.parameter_names},
             {"parameter_bounds", bounds},
             {"marginalization", d.marginalization},
             {"random_dimension", d.random_dimension},
             {"ordered", d.ordered},
             {"max_unit_rows", d.unit_limit},
             {"derivative_orders", d.derivative_orders},
             {"predict", prediction},
             {"forecast", forecast}};
  value["digest"] = sha256(build_id() + "\n" + value.dump());
  return value;
}
inline void lexical_integer_bounds(const std::string &source) {
  std::size_t i = 0;
  while (i < source.size()) {
    if (source[i] == '"') {
      ++i;
      while (i < source.size()) {
        if (source[i] == '\\') {
          i += 2;
          continue;
        }
        if (source[i++] == '"')
          break;
      }
    } else if (source[i] == '-' || (source[i] >= '0' && source[i] <= '9')) {
      const std::size_t start = i++;
      while (i < source.size() &&
             ((source[i] >= '0' && source[i] <= '9') || source[i] == '.' ||
              source[i] == 'e' || source[i] == 'E' || source[i] == '+' ||
              source[i] == '-'))
        ++i;
      const std::string token = source.substr(start, i - start);
      if (token.find_first_of(".eE") == std::string::npos) {
        std::from_chars_result result;
        if (token[0] == '-') {
          std::int64_t value = 0;
          result =
              std::from_chars(token.data(), token.data() + token.size(), value);
          require(result.ec == std::errc() && value >= -9007199254740991LL,
                  "Integer token exceeds the common safe-integer interval",
                  "INVALID_JSON");
        } else {
          std::uint64_t value = 0;
          result =
              std::from_chars(token.data(), token.data() + token.size(), value);
          require(result.ec == std::errc() && value <= 9007199254740991ULL,
                  "Integer token exceeds the common safe-integer interval",
                  "INVALID_JSON");
        }
        require(result.ec == std::errc() &&
                    result.ptr == token.data() + token.size(),
                "Integer token exceeds the supported exact contract",
                "INVALID_JSON");
      }
    } else
      ++i;
  }
}
inline std::size_t unicode_scalars(const std::string &value) {
  // nlohmann validates UTF-8 and escaped surrogate pairs before this callback.
  return static_cast<std::size_t>(
      std::count_if(value.begin(), value.end(),
                    [](unsigned char c) { return (c & 0xc0) != 0x80; }));
}
inline Json parse_json(const std::string &source) {
  lexical_integer_bounds(source);
  std::vector<std::set<std::string>> object_keys;
  auto callback = [&](int depth, Json::parse_event_t event, Json &value) {
    require(depth <= 32, "JSON nesting exceeds its bound", "INVALID_JSON");
    if (event == Json::parse_event_t::object_start)
      object_keys.emplace_back();
    if (event == Json::parse_event_t::key) {
      require(unicode_scalars(value.get_ref<const std::string &>()) <= 256,
              "JSON key exceeds its scalar bound", "INVALID_JSON");
      require(!object_keys.empty() && object_keys.back().size() < 1024 &&
                  object_keys.back().insert(value.get<std::string>()).second,
              "Duplicate or excessive JSON object keys", "INVALID_JSON");
    }
    if (event == Json::parse_event_t::value && value.is_string())
      require(unicode_scalars(value.get_ref<const std::string &>()) <=
                  1'000'000,
              "JSON string exceeds its scalar bound", "INVALID_JSON");
    if (event == Json::parse_event_t::array_end)
      require(value.size() <= 8192, "JSON array exceeds its bound",
              "INVALID_JSON");
    if (event == Json::parse_event_t::object_end)
      object_keys.pop_back();
    return true;
  };
  try {
    return Json::parse(source, callback);
  } catch (const Json::exception &) {
    throw Error("INVALID_JSON", "Malformed UTF-8 JSON request");
  }
}
inline double number(const Json &value) {
  require(value.is_number(), "Expected a numeric value");
  if (value.is_number_unsigned()) {
    require(value.get<std::uint64_t>() <= 9007199254740991ULL,
            "Integer exceeds the common safe-integer interval");
  } else if (value.is_number_integer()) {
    const auto n = value.get<std::int64_t>();
    const auto magnitude = n < 0 ? static_cast<std::uint64_t>(-(n + 1)) + 1
                                 : static_cast<std::uint64_t>(n);
    require(magnitude <= 9007199254740991ULL,
            "Integer exceeds the common safe-integer interval");
  }
  const double result = value.get<double>();
  finite(result);
  return result;
}
inline Vector numbers(const Json &array, std::size_t limit) {
  require(array.is_array() && array.size() <= limit,
          "Expected a bounded numeric array");
  Vector result;
  result.reserve(array.size());
  for (const auto &value : array)
    result.push_back(number(value));
  return result;
}
inline Rows matrix(const Json &array, std::size_t width, std::size_t limit) {
  require(array.is_array() && array.size() <= limit,
          "Expected a bounded numeric row matrix");
  Rows result;
  result.reserve(array.size());
  for (const auto &row : array) {
    require(row.is_array() && row.size() == width,
            "Numeric row has the wrong field count");
    result.push_back(numbers(row, max_fields));
  }
  return result;
}
inline bool safe_identifier(const Json &value, std::size_t maximum = 128) {
  if (!value.is_string())
    return false;
  const auto &s = value.get_ref<const std::string &>();
  return !s.empty() && s.size() <= maximum &&
         std::all_of(s.begin(), s.end(),
                     [](unsigned char c) { return c >= 32 && c <= 126; });
}
inline void keys(const Json &request, std::set<std::string> required,
                 const std::set<std::string> &optional = {}) {
  require(request.is_object(), "Request must be an object");
  for (const auto &item : request.items())
    require(required.erase(item.key()) != 0 || optional.count(item.key()),
            "Unsupported request field");
  require(required.empty(), "Required request field is missing");
}
class Protocol {
  std::vector<Model> models_ = prepared_models();

public:
  Json describe() const {
    Json models = Json::array();
    for (const auto &model : models_)
      models.push_back(descriptor_json(model.descriptor));
    return {{"protocol", 1},
            {"build_id", build_id()},
            {"engine", engine_identity()},
            {"models", models}};
  }
  Json handle(const Json &request, const std::string &hash) const {
    require(request.is_object() && request.contains("protocol") &&
                request["protocol"].is_number_integer() &&
                !request["protocol"].is_boolean() && request["protocol"] == 1,
            "Unsupported protocol version");
    require(request.contains("request_id") &&
                safe_identifier(request["request_id"]),
            "Invalid request identity");
    require(request.contains("op") && safe_identifier(request["op"], 32),
            "Invalid operation");
    const auto id = request["request_id"].get<std::string>(),
               op = request["op"].get<std::string>();
    Json response{{"protocol", 1},
                  {"request_id", id},
                  {"request_sha256", hash},
                  {"status", "ok"},
                  {"build_id", build_id()}};
    if (op == "describe") {
      keys(request, {"protocol", "request_id", "op"});
      const auto description = describe();
      response["engine"] = description["engine"];
      response["models"] = description["models"];
      return response;
    }
    require(op == "evaluate" || op == "predict" || op == "forecast",
            "Unknown fixed operation", "UNSUPPORTED_OPERATION");
    const std::set<std::string> common{"protocol", "request_id",   "op",
                                       "model_id", "model_digest", "theta",
                                       "rows"};
    require(request.contains("model_id") &&
                safe_identifier(request["model_id"], 64),
            "Invalid model ID");
    const auto found =
        std::find_if(models_.begin(), models_.end(), [&](const Model &m) {
          return m.descriptor.id == request["model_id"].get<std::string>();
        });
    require(found != models_.end(), "Unknown prepared model", "MODEL_IDENTITY");
    const auto &model = *found;
    const auto descriptor = descriptor_json(model.descriptor);
    response["model_id"] = model.descriptor.id;
    response["model_digest"] = descriptor["digest"];
    require(request.contains("model_digest") &&
                request["model_digest"].is_string() &&
                request["model_digest"] == descriptor["digest"],
            "Prepared model digest differs", "MODEL_IDENTITY");
    require(request.contains("theta") && request.contains("rows"),
            "Model data or parameters are missing");
    const auto theta = numbers(request["theta"], max_parameters);
    if (op == "evaluate") {
      const bool unit = model.descriptor.fit_kind == "unit";
      auto required = common;
      required.insert("kind");
      required.insert(unit ? "unit_weight" : "weights");
      keys(request, required, {"hessian"});
      require(request["kind"].is_string() &&
                  request["kind"] == (unit ? "unit" : "rows"),
              "Evaluation factorization differs");
      require(!request.contains("hessian") || request["hessian"].is_boolean(),
              "Hessian flag must be boolean");
      const bool hessian = request.value("hessian", false);
      require(!hessian ||
                  std::find(model.descriptor.derivative_orders.begin(),
                            model.descriptor.derivative_orders.end(),
                            2) != model.descriptor.derivative_orders.end(),
              "Requested derivative order is not declared",
              "UNSUPPORTED_OPERATION");
      Data data{matrix(request["rows"], model.descriptor.fit_fields.size(),
                       unit ? model.descriptor.unit_limit : max_rows),
                {}};
      double weight = 1;
      if (unit)
        weight = number(request["unit_weight"]);
      else
        data.weights = numbers(request["weights"], max_rows);
      const auto result = evaluate(model, theta, data, weight, hessian);
      response.update({{"loss", result.loss},
                       {"gradient", result.gradient},
                       {"row_count", result.row_count},
                       {"unit_count", result.unit_count},
                       {"weight_sum", result.weight_sum}});
      if (hessian)
        response["hessian"] = result.hessian;
      response["diagnostics"] = {
          {"marginalization", model.descriptor.marginalization}};
      if (result.diagnostics.used) {
        const auto &d = result.diagnostics;
        response["diagnostics"].update(
            {{"mode", d.mode},
             {"inner_score_inf", d.score_inf},
             {"inner_iterations", d.iterations},
             {"inner_line_search_steps", d.line_search_steps},
             {"damping_steps", d.damping_steps},
             {"roundoff_corrections", d.roundoff_corrections},
             {"minimum_eigenvalue", d.minimum_eigenvalue},
             {"maximum_eigenvalue", d.maximum_eigenvalue},
             {"mode_scope", "local stationary mode with positive curvature; no "
                            "global-mode guarantee"}});
      }
    } else {
      auto required = common;
      required.insert("target");
      if (op == "forecast")
        required.insert("history");
      keys(request, required,
           op == "predict" ? std::set<std::string>{"history"}
                           : std::set<std::string>{});
      require(safe_identifier(request["target"], 64),
              "Invalid prediction target");
      const auto name = request["target"].get<std::string>();
      const bool forecast = op == "forecast";
      const auto &target = find_target(model, name, forecast);
      const auto rows = matrix(request["rows"], target.fields.size(),
                               forecast || model.descriptor.fit_kind == "unit"
                                   ? model.descriptor.unit_limit
                                   : max_rows);
      const auto history =
          request.contains("history")
              ? matrix(request["history"], model.descriptor.fit_fields.size(),
                       model.descriptor.unit_limit)
              : Rows{};
      const auto result = predict(model, theta, rows, history, name, forecast);
      response.update({{"columns", target.columns},
                       {"values", result.values},
                       {"row_count", rows.size()},
                       {"conditioning", target.conditioning},
                       {"uncertainty", target.uncertainty}});
    }
    return response;
  }
};
inline void write_frame(const Json &value) {
  const std::string payload = value.dump();
  require(payload.size() <= frame_limit, "Output exceeded frame bound",
          "RESOURCE_LIMIT");
  const auto n = static_cast<std::uint32_t>(payload.size());
  const std::array<char, 4> header{
      static_cast<char>((n >> 24) & 255), static_cast<char>((n >> 16) & 255),
      static_cast<char>((n >> 8) & 255), static_cast<char>(n & 255)};
  std::cout.write(header.data(), 4);
  std::cout.write(payload.data(), static_cast<std::streamsize>(payload.size()));
  std::cout.flush();
  require(static_cast<bool>(std::cout), "Output transport failed",
          "TRANSPORT_ERROR");
}
} // namespace ds60_tmbad
