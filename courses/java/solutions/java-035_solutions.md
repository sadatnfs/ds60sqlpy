# java-035: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A small data service combines domain rules,storage andtransport contracts. Its correctness is more than a200status:the response grain,columns,ordering,error semantics andresource lifetime must agree. This capstone serves a read-only grouped summary over three authored records. Storage is anexplicit in-memory repository,not a simulatedJDBCclaim. The earlierJDBC lesson separately exercised a real database.

The service binds only toloopback on anephemeralport andstops when theownedfixture closes. It accepts oneGETroute withonegroupqueryparameter. The group must be a single uppercaseletter;unknown validgroups return404,malformedqueries return400,andunsupportedmethods return405. The domain summary is tested directly andthrough actualHTTPrequests. This is a bounded local service demonstration,not a deployed authenticated application.

**Response grain:** The identity of one row orobject in a service result.

**Repository port:** The contract through which domain logic reads stored records.

**HTTP adapter:** Code translating validated requests into domain calls andresponses.

**Contract test:** A check of observable behavior across a component boundary.

## Reading the reference

ARepository port exposes animmutable row list. The pure summary function filters bygroup andreturns count andinteger total. TheHTTPadapter validates exactpath,method andquerystructure beforecalling thecore. Since the admitted group is one uppercaseASCIIletter,thefixedJSONencoder cannot be influenced by arbitraryquotes. HttpClient requests use timeouts,and everyexchange,responsebody andserverinstance isclosed.

## Exercise 1: Verify the domain summary

Task: SummarizegroupAoveramounts10,20 andgroupBover5.

The domain result has one objectperrequestedgroup. It is checked independently ofHTTPformatting andstatus handling.

```java
Repository repository=() -> List.of(new Row("a1","A",10),new Row("a2","A",20),new Row("b1","B",5));
assert summarize(repository,"A").equals(new Summary("A",2,30));assert summarize(repository,"B").equals(new Summary("B",1,5));
```

**Expected:** Acount2,total30;Bcount1,total5.

**Verify:** Compare the program values or named exception with Acount2,total30;Bcount1,total5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Read a successful HTTPsummary

Task: GET/summary?group=Afromtheownedserver.

The exact body check fixes the publicschema andinteger representation. The source counts remain independently known.

```java
try(DataServer server=new DataServer(repository);var client=java.net.http.HttpClient.newHttpClient()) {
    var response=send(client,server.uri("/summary?group=A"),"GET");
    assert response.statusCode()==200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}");
}
```

**Expected:** status200 andexactJSONwithcount2,total30.

**Verify:** Compare the program values or named exception with status200 andexactJSONwithcount2,total30. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Report an unknown validgroup

Task: GETgroupC,whichpasses syntax buthasnorecords.

A valid butabsent domainidentity differs frommalformedinput. Keeping thestatus distinction helpsclients respond appropriately.

```java
try(DataServer server=new DataServer(repository);var client=java.net.http.HttpClient.newHttpClient()) {
    var response=send(client,server.uri("/summary?group=C"),"GET");assert response.statusCode()==404 && response.body().contains("not_found");
}
```

**Expected:** status404 withnot_found error.

**Verify:** Compare the program values or named exception with status404 withnot_found error. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject ambiguous ormalformedqueries

Task: Sendduplicategroupparameters andalowercasegroup.

The adapter refuses toguess whichduplicatevaluewins. A broaderquerygrammar wouldneed anexplicit parser andvalidation policy.

```java
try(DataServer server=new DataServer(repository);var client=java.net.http.HttpClient.newHttpClient()) {
    assert send(client,server.uri("/summary?group=A&group=B"),"GET").statusCode()==400;
    assert send(client,server.uri("/summary?group=a"),"GET").statusCode()==400;
}
```

**Expected:** bothstatus400.

**Verify:** Compare the program values or named exception with bothstatus400. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject unsupportedmethods andpathlookalikes

Task: POSTtothesummaryroute andGET/summary-extra.

The underlyingserverusesprefixcontexts,so theadaptermustenforceitsownexactpathcontract. No writeoperation isexposed.

```java
try(DataServer server=new DataServer(repository);var client=java.net.http.HttpClient.newHttpClient()) {
    assert send(client,server.uri("/summary?group=A"),"POST").statusCode()==405;
    assert send(client,server.uri("/summary-extra?group=A"),"GET").statusCode()==404;
}
```

**Expected:** 405 and404 respectively.

**Verify:** Compare the program values or named exception with 405 and404 respectively. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Preserve storage andclose theownedlistener

Task: Comparetherepositorybefore/afterrequests andclose theserver.

The read-onlyservice shouldnotmutate itsstorage. Thefixture owns thelistener anddoesnotleave a backgrounddeployment running.

```java
List<Row> before=repository.rows();DataServer server=new DataServer(repository);server.close();
assert server.closed && repository.rows().equals(before) && repository.rows().size()==3;
```

**Expected:** 3unchangedrecords;closedflagtrue.

**Verify:** Compare the program values or named exception with 3unchangedrecords;closedflagtrue. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
