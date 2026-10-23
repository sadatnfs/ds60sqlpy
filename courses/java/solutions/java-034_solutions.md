# java-034: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Application design separates domain decisions from the mechanisms that supply data,time orside effects. A pure pricing calculation can be tested without a database,network orsystemclock. A service composes that calculation with repository andclock ports. Adapters implement those ports for a particular environment. Dependency inversion means the domain-facing code depends on thebehavior it needs rather than on a concrete infrastructure class.

This lesson builds a small quote service. A catalog port supplies integer-cent prices,a fixed clock supplies thetimestamp,and an audit sink records successful operations in memory. The service validates quantity andcatalog lookup before producing a result orrecording anevent. A failing repository propagates its failure ratherthan returning a fabricatedzero price. Thefake-backed tests establish service logic andcall boundaries,not live database ornetwork acceptance.

**Port:** A behavior interface required by application logic.

**Adapter:** An implementation connecting a port to a concrete mechanism.

**Pure core:** Domain calculations independent of infrastructure side effects.

**Dependency inversion:** Depending on required behavior rather than concrete external machinery.

## Reading the reference

Define aCatalog interface returningOptionalLong anddeclaringIOException for anoperational read failure. Inject aSupplier<Instant> andConsumer<String> through theconstructor. Keep thepure total calculation separate anduseMath.multiplyExact foroverflow. TheQuote record carries item,quantity,total andtime. Audit only afterall requiredvalidation andcalculation succeed.

## Exercise 1: Test the pure calculation

Task: Compute3items at125cents andcheckzero/negativequantity policy.

The core arithmetic needsno repository orclock. Isolating it makes domain boundaries andoverflow behavior easy tocheck.

```java
assert total(3,125)==375;boolean invalid=false;try{total(0,125);}catch(IllegalArgumentException expected){invalid=true;}assert invalid;
```

**Expected:** 375cents;nonpositivequantityrejected.

**Verify:** Compare the program values or named exception with 375cents;nonpositivequantityrejected. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Compose a deterministic service

Task: Inject a fixedcatalog,clock andauditlist,andrequest twoitems.

A fixed clock removes timing nondeterminism. The audit event is a local test double,not a message sent to another person orservice.

```java
List<String> audit=new ArrayList<>();var instant=java.time.Instant.parse("2026-01-01T00:00:00Z");
Catalog catalog=id -> id.equals("item-a")?java.util.OptionalLong.of(125):java.util.OptionalLong.empty();
Service service=new Service(catalog,() -> instant,audit::add);Quote quote=service.quote("item-a",2);
assert quote.totalCents()==250 && quote.created().equals(instant) && audit.equals(List.of("quoted:item-a"));
```

**Expected:** total250,time2026-01-01T00:00:00Z,oneauditevent.

**Verify:** Compare the program values or named exception with total250,time2026-01-01T00:00:00Z,oneauditevent. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Reject an unknown catalog item

Task: Requestmissing andinspecttheauditlist.

A missing item is a domain outcome. It shouldnot silently become a zero-priced quote orproduce a misleading success event.

```java
boolean missing=false;try{service.quote("missing",2);}catch(NoSuchElementException expected){missing=true;}
assert missing && audit.size()==1;
```

**Expected:** NoSuchElementException;noadditionalaudit.

**Verify:** Compare the program values or named exception with NoSuchElementException;noadditionalaudit. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Propagate an infrastructure failure

Task: Inject aCatalog thatthrowsIOException.

An operational failure differs from a valid missing lookup. The service preserves that distinction so a caller can choose retry orerror behavior appropriately.

```java
List<String> failures=new ArrayList<>();Service unavailable=new Service(id -> {throw new java.io.IOException("catalog unavailable");},() -> instant,failures::add);boolean propagated=false;
try{unavailable.quote("item-a",1);}catch(java.io.IOException expected){propagated=expected.getMessage().equals("catalog unavailable");}
assert propagated && failures.isEmpty();
```

**Expected:** samefailuretype;nosuccessaudit.

**Verify:** Compare the program values or named exception with samefailuretype;nosuccessaudit. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Prove invalid quantity fails before a repository call

Task: Use a countingcatalog andrequestnegativequantity.

Validation ordering is part of theboundary contract. It avoids unnecessary externalwork andprevents a malformedrequest from being mistaken for an infrastructure failure.

```java
var calls=new java.util.concurrent.atomic.AtomicInteger();Service checked=new Service(id -> {calls.incrementAndGet();return java.util.OptionalLong.of(1);},() -> instant,value -> {});boolean rejected=false;
try{checked.quote("item-a",-1);}catch(IllegalArgumentException expected){rejected=true;}
assert rejected && calls.get()==0;
```

**Expected:** repositorycallcount0.

**Verify:** Compare the program values or named exception with repositorycallcount0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Detect arithmetic overflow without an event

Task: UseLong.MAX_VALUEunitprice andquantity2.

A validly typed integer canstill exceed thedomain representation. Calculating before emitting a success event keeps side effects aligned with theactual outcome.

```java
List<String> overflowAudit=new ArrayList<>();Service expensive=new Service(id -> java.util.OptionalLong.of(Long.MAX_VALUE),() -> instant,overflowAudit::add);boolean overflow=false;
try{expensive.quote("x",2);}catch(ArithmeticException expected){overflow=true;}
assert overflow && overflowAudit.isEmpty();
```

**Expected:** ArithmeticException;auditsinkunused.

**Verify:** Compare the program values or named exception with ArithmeticException;auditsinkunused. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
