import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Preserve an instant across zones
    var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
    var utc = instant.atZone(java.time.ZoneId.of("UTC"));
    var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
    assert utc.toInstant().equals(ny.toInstant()) &&
    ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31));

    // Exercise 2: Compare calendar and elapsed days
    var start = java.time.ZonedDateTime.of(
      2024,
      3,
      9,
      12,
      0,
      0,
      0,
      java.time.ZoneId.of("America/New_York")
    );
    var nextDay = start.plusDays(1);
    var next24 = start.plusHours(24);
    assert java.time.Duration.between(start, nextDay).toHours() == 23;
    assert nextDay.getHour() == 12 && next24.getHour() == 13;

    // Exercise 3: Detect a nonexistent local time
    var zone = java.time.ZoneId.of("America/New_York");
    var gap = java.time.LocalDateTime.of(2024, 3, 10, 2, 30);
    assert zone.getRules().getValidOffsets(gap).isEmpty();

    // Exercise 4: Detect an ambiguous local time
    var overlap = java.time.LocalDateTime.of(2024, 11, 3, 1, 30);
    assert zone.getRules().getValidOffsets(overlap).size() == 2;

    // Exercise 5: Parse a strict calendar date
    assert java.time.LocalDate.parse("2024-02-29").getDayOfMonth() == 29;
    boolean invalid = false;
    try {
      java.time.LocalDate.parse("2023-02-29");
    } catch (java.time.format.DateTimeParseException expected) {
      invalid = true;
    }
    assert invalid;

    // Exercise 6: Use a half-open time window
    var end = instant.plusSeconds(3600);
    assert !instant.isBefore(instant) && instant.isBefore(end);
    assert !(!end.isBefore(instant) && end.isBefore(end));
  }
}
