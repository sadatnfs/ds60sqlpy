// SPDX-License-Identifier: MIT
#include "ds60_tmbad/protocol.hpp"
#include "ds60_tmbad/sandbox.hpp"

int main(int argc, char **argv) {
  using namespace ds60_tmbad;
  if (argc != 2 || (std::string(argv[1]) != "--stdio" &&
                    std::string(argv[1]) != "--describe")) {
    std::cerr << "Use the fixed --stdio or --describe operation\n";
    return 64;
  }
  std::signal(SIGPIPE, SIG_IGN);
  try {
    process_guards();
  } catch (const std::exception &) {
    std::cerr << "Native process preparation failed\n";
    return 2;
  }
  std::unique_ptr<Protocol> prepared;
  try {
    prepared = std::make_unique<Protocol>();
  } catch (const std::exception &) {
    std::cerr << "Prepared registry initialization failed\n";
    return 2;
  }
  const auto &protocol = *prepared;
  if (std::string(argv[1]) == "--describe") {
    try {
      std::cout << protocol.describe().dump() << '\n';
      return std::cout ? 0 : 2;
    } catch (const std::exception &) {
      std::cerr << "Prepared model description failed\n";
      return 2;
    }
  }
  while (true) {
    std::string id, payload, hash;
    Json request;
    try {
      std::array<unsigned char, 4> header{};
      std::cin.read(reinterpret_cast<char *>(header.data()), 4);
      if (std::cin.gcount() == 0 && std::cin.eof())
        return 0;
      require(std::cin.gcount() == 4, "Partial frame header", "INVALID_FRAME");
      const std::uint32_t size = (std::uint32_t(header[0]) << 24) |
                                 (std::uint32_t(header[1]) << 16) |
                                 (std::uint32_t(header[2]) << 8) | header[3];
      require(size > 0 && size <= frame_limit, "Frame length exceeds its bound",
              "INVALID_FRAME");
      payload.resize(size);
      std::cin.read(payload.data(), static_cast<std::streamsize>(size));
      payload.resize(static_cast<std::size_t>(std::cin.gcount()));
      hash = sha256(payload);
      require(payload.size() == size, "Partial frame payload", "INVALID_FRAME");
      request = parse_json(payload);
      if (request.is_object() && request.contains("request_id") &&
          safe_identifier(request["request_id"]))
        id = request["request_id"].get<std::string>();
      write_frame(protocol.handle(request, hash));
    } catch (const std::exception &error) {
      const auto *typed = dynamic_cast<const Error *>(&error);
      const std::string code = typed ? typed->code
                               : dynamic_cast<const std::bad_alloc *>(&error)
                                   ? "RESOURCE_LIMIT"
                                   : "INTERNAL_ERROR";
      const std::string message =
          typed ? std::string(typed->what()).substr(0, 512)
                : "Native request failed";
      try {
        if (hash.empty())
          hash = sha256(payload);
        Json result{{"protocol", 1},
                    {"request_id", id},
                    {"request_sha256", hash},
                    {"status", "error"},
                    {"build_id", build_id()},
                    {"error", {{"code", code}, {"message", message}}}};
        if (request.is_object() && request.contains("model_id") &&
            safe_identifier(request["model_id"], 64))
          result["model_id"] = request["model_id"];
        if (request.is_object() && request.contains("model_digest") &&
            request["model_digest"].is_string() &&
            hex_digest(request["model_digest"].get<std::string>()))
          result["model_digest"] = request["model_digest"];
        write_frame(result);
      } catch (...) {
        std::cerr << "Native request terminated without a response frame\n";
      }
      return 2;
    }
  }
}
