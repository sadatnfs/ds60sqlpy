# java-033: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An application boundary converts untrusted input into a limited set of permitted operations. Type andsyntax checks are necessary butnot sufficient:an identifier can be avalidString while naming an unauthorized file,andan accepted operation can still consume unbounded resources. Prefer explicit operation andidentifier allowlists when the task is small. Keep validation close to the resource use andreport a named failure instead of silently choosing a broader fallback.

Filesystem containment has both lexical andreal-path concerns. Normalizing awaydot segments can detect a simpleparent traversal,but a symbolic link can redirect a seemingly contained path. This lesson uses anowned temporary directory andknown fixtures,checks both forms ofcontainment,andbounds reads withlimit+1 bytes. It doesnot claim to be a race-proof sandbox against a concurrent adversary changing the filesystem. Logs retain selected metadata rather than copying secrets orrawsource bodies.

**Allowlist:** An explicit set of admitted operations oridentifiers.

**Path containment:** A check that a resource remains within its declared owned root.

**Resource bound:** A limit enforced before unbounded allocation orwork.

**Safe diagnostic:** A useful failure record that excludes unnecessary sensitive content.

## Reading the reference

Resolve a relativepath under a real root,normalize it,andreject absolute orescaping paths. Reject symbolic-linkcomponents under thissimplepolicy,thencheck theexisting realpath remains inside theroot. Read atmostlimit+1bytes andreject anoversizedpayload. A fixed dispatcher maps admitted operationnames to knownfunctions;it neverpasses input to a shell orreflection loader. Build logs from anallowlistedmetadata schema.

## Exercise 1: Read an admitted owned file

Task: Createinput.txt inside anownedroot andread atmost10bytes.

The helper reads actual localbytes under a bounded contract. The fixture root is owned by thelesson andcontains no user data.

```java
withRoot(root -> {java.nio.file.Files.writeString(root.resolve("input.txt"),"hello");assert new String(readBounded(root,"input.txt",10),java.nio.charset.StandardCharsets.UTF_8).equals("hello");});
```

**Expected:** contenthello.

**Verify:** Compare the program values or named exception with contenthello. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Reject lexical traversal andabsolute paths

Task: Attempt../outside.txt andanabsolutechildpath.

A path's string appearance isnot a permission decision. Normalization andrelative-path validation make the simple boundary explicit.

```java
withRoot(root -> {
    for(String name:List.of("../outside.txt",root.resolve("input.txt").toString())){boolean rejected=false;try{readBounded(root,name,10);}catch(SecurityException expected){rejected=true;}assert rejected;}
});
```

**Expected:** SecurityException forboth.

**Verify:** Compare the program values or named exception with SecurityException forboth. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Enforce the byte limit after reading a bounded amount

Task: Writefivebytes andrequest a four-byte maximum.

A preflightFiles.size checkalonecanrace withfilegrowth. Readingonlylimit+1bytes keepsallocationbounded anddetects anoversizedresult.

```java
withRoot(root -> {java.nio.file.Files.writeString(root.resolve("large.txt"),"abcde");boolean rejected=false;try{readBounded(root,"large.txt",4);}catch(java.io.IOException expected){rejected=expected.getMessage().contains("limit");}assert rejected;});
```

**Expected:** IOException foroversizedcontent.

**Verify:** Compare the program values or named exception with IOException foroversizedcontent. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject symbolic-link access under the declared policy

Task: Create a link inside theownedroot toanotherownedfile andattempt toread throughit.

The default policy rejects allsymlink components,even anin-root target. A morepermissive policy needsadditional ownership andrace analysis ratherthan simply skipping thecheck.

```java
withRoot(root -> {
    java.nio.file.Files.writeString(root.resolve("target.txt"),"fixture");boolean created=false;
    try{java.nio.file.Files.createSymbolicLink(root.resolve("link.txt"),java.nio.file.Path.of("target.txt"));created=true;}catch(UnsupportedOperationException|java.io.IOException unavailable){System.out.println("symbolic-link fixture unavailable on this platform");}
    if(created){boolean rejected=false;try{readBounded(root,"link.txt",20);}catch(SecurityException expected){rejected=true;}assert rejected;}
});
```

**Expected:** link rejected when platform supports creation;unsupported capability recorded explicitly.

**Verify:** Compare the program values or named exception with link rejected when platform supports creation;unsupported capability recorded explicitly. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Keep operation names out ofcode execution

Task: Admitonlyread_fixture andrejectrun_shell.

The inputselects among fixed behavior;it doesnot become executabletext. A model proposal orretrieved instruction cannot expand thiscatalog.

```java
Map<String,String> operations=Map.of("read_fixture","fixed local reader");assert operations.containsKey("read_fixture");boolean rejected=false;
try{if(!operations.containsKey("run_shell"))throw new IllegalArgumentException("operation not allowed");}catch(IllegalArgumentException expected){rejected=true;}
assert rejected;
```

**Expected:** unknownoperationIllegalArgumentException.

**Verify:** Compare the program values or named exception with unknownoperationIllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Build a restricted diagnostic record

Task: Copy onlyrequest_id,operation andstatus from a map containingtoken andsource_text.

Logs areanotherdata surface. Selecting metadata deliberately ismore reliable than assuming everyrawinput is safe toprint.

```java
Map<String,String> raw=Map.of("request_id","r1","operation","read_fixture","status","rejected","token","do-not-log","source_text","private fixture");
Map<String,String> safe=Map.of("request_id",raw.get("request_id"),"operation",raw.get("operation"),"status",raw.get("status"));
assert !safe.containsKey("token") && !safe.containsKey("source_text") && safe.size()==3;
```

**Expected:** diagnostic excludes both sensitive fields.

**Verify:** Compare the program values or named exception with diagnostic excludes both sensitive fields. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
