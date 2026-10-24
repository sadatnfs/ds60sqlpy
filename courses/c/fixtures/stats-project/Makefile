CC ?= cc
CPPFLAGS ?=
CFLAGS ?= -O2
CFLAGS += -std=c17 -Wall -Wextra -Wpedantic
LDFLAGS ?=
BUILD_DIR ?= build

.PHONY: all test sanitize clean
all: $(BUILD_DIR)/stats-demo

$(BUILD_DIR):
	mkdir -p "$(BUILD_DIR)"

$(BUILD_DIR)/stats.o: stats.c stats.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c stats.c -o "$@"

$(BUILD_DIR)/main.o: main.c stats.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c main.c -o "$@"

$(BUILD_DIR)/stats-demo: $(BUILD_DIR)/main.o $(BUILD_DIR)/stats.o
	$(CC) $(LDFLAGS) "$(BUILD_DIR)/main.o" "$(BUILD_DIR)/stats.o" -o "$@"

$(BUILD_DIR)/stats-test: stats_test.c stats.h $(BUILD_DIR)/stats.o
	$(CC) $(CPPFLAGS) $(CFLAGS) stats_test.c "$(BUILD_DIR)/stats.o" $(LDFLAGS) -o "$@"

test: $(BUILD_DIR)/stats-test
	"$(BUILD_DIR)/stats-test"

sanitize: | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) -std=c17 -Wall -Wextra -Wpedantic -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer stats.c stats_test.c -o "$(BUILD_DIR)/stats-test-sanitized"
	"$(BUILD_DIR)/stats-test-sanitized"

clean:
	rm -f "$(BUILD_DIR)/stats.o" "$(BUILD_DIR)/main.o" "$(BUILD_DIR)/stats-demo" "$(BUILD_DIR)/stats-test" "$(BUILD_DIR)/stats-test-sanitized"
