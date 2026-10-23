# java-036: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A release is a reproducible artifact plus evidence about how it starts,what contracts it accepts andhow failures are diagnosed. Source compilation alone doesnot prove that packaging preserved theentrypoint orthat thetargetruntime supports theclass version. Hashes identify artifactbytes,but avalidhash doesnot establish correct behavior. A deliberate failing integrity check proves that thegate isconnected to thedecision rather than merely printing a success label.

This capstone builds a smallJava21JAR witha fixedtimestamp,checks class-file version65,executes a self-test in a freshJVM andrejects bothaninvalidlaunchargument andtamperedartifactbytes. It retains a previous-artifact identity in therelease record. jlink is explained as a separate custom-runtime packaging step;thedefault reference only probes toolavailability anddoesnotbuild a large runtime image inside thebounded browser job. Production deployment andoperational acceptance remain separate from this localartifact check.

**Release artifact:** The packaged program andmetadata intended fordistribution.

**Class-file version:** The bytecode format level required by aJVM.

**Integrity gate:** A check thatartifactbytes match theexpectedidentity.

**Custom runtime image:** A platform-specificJava runtime assembled fromselectedmodules.

## Reading the reference

Use thepreparedcompiler with--release21,then inspect theclass magic andmajorversion throughDataInputStream. Package withtheJDKjar tool andanexplicitMain-Class. Launch theartifact using a fixedlocaljava executable withboundedwait andcapturedoutput. SHA256 verification occurs before execution. A manualjlink recipe mustname requiredmodules,anownedoutputdirectory andactualplatform;itcannot create one universalruntime for everyOS/architecture. The child process inherits the prepared environment unchanged. JVM startup notices such as JAVA_TOOL_OPTIONS belong to stderr, while the application result belongs to stdout. Capture both streams separately in owned files so diagnostics cannot corrupt an exact output comparison; include stderr when a child fails. Do not remove inherited CPU or resource settings to make a test pass.

## Exercise 1: Verify the compiler target

Task: Compile thefixture with--release21 andinspect itsclassheader.

The header is direct evidence ofthetargetbytecode level. Afilename orREADMEclaim cannot replace it.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {
    fixture.build();try(var input=new java.io.DataInputStream(java.nio.file.Files.newInputStream(fixture.classes.resolve("App.class")))){assert input.readInt()==0xCAFEBABE;input.readUnsignedShort();assert input.readUnsignedShort()==65;}
}
```

**Expected:** magicCAFEBABE;majorversion65.

**Verify:** Compare the program values or named exception with magicCAFEBABE;majorversion65. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Inspect packaged launch metadata

Task: Open thebuiltJAR andcheckMain-Class andApp.class.

Packaging canfail independently ofcompilation. The archive mustcontain theintendedentrypoint andmatchingmetadata.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {
    fixture.build();try(var jar=new java.util.jar.JarFile(fixture.jar.toFile())){assert jar.getManifest().getMainAttributes().getValue("Main-Class").equals("App") && jar.getJarEntry("App.class")!=null;}
}
```

**Expected:** Main-ClassApp;classentrypresent.

**Verify:** Compare the program values or named exception with Main-ClassApp;classentrypresent. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Run a fresh-process self-test

Task: Launch theJAR with--self-test through a bounded childJVM.

The newprocess cannotreuseclasses loaded bytheauthoring program. Thischecks theactualpackagedlaunch path.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {fixture.build();Run result=fixture.run("--self-test");assert result.code()==0 && result.output().strip().equals("release-ok");}
```

**Expected:** exit0 andoutputrelease-ok.

**Verify:** Compare the program values or named exception with exit0 andoutputrelease-ok. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Verify an invalid launch fails clearly

Task: Run thesameJAR withanunsupportedargument.

An acceptance suite shouldinclude a meaningfulfailure path. Returningexit0 for everyargument would make automation unable todistinguish misuse.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {fixture.build();Run result=fixture.run("--unsupported");assert result.code()==2 && result.error().contains("unknown argument");}
```

**Expected:** exit2 andunknown argument diagnostic.

**Verify:** Compare the program values or named exception with exit2 andunknown argument diagnostic. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject artifact tampering before execution

Task: Hash theJAR,fliponebyte,andcalltheintegrity gate.

The corruptartifact isneverexecuted. Ahashcheck verifiesbyteidentity,while theself-test separately verifiesbehavior.

```java
try(ReleaseFixture fixture=new ReleaseFixture()) {
    fixture.build();byte[] original=java.nio.file.Files.readAllBytes(fixture.jar);byte[] expected=sha256(original);byte[] changed=original.clone();changed[0]^=1;java.nio.file.Files.write(fixture.jar,changed);boolean rejected=false;
    try{verify(fixture.jar,expected);}catch(SecurityException failure){rejected=true;}finally{java.nio.file.Files.write(fixture.jar,original);}
    assert rejected;verify(fixture.jar,expected);
}
```

**Expected:** SecurityException;originalbytesrestored forcleanup.

**Verify:** Compare the program values or named exception with SecurityException;originalbytesrestored forcleanup. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Record runtime-image scope androllback identity

Task: Inspectwhetherjlinkexists,andwrite a record distinguishinglocalJARacceptance fromanunbuiltcustomruntime.

Toolpresence isnot a runtime-image buildreceipt. Amanualjlink buildneeds itsownmoduleclosure,platform,launch andfailure checks beforedistribution.

```java
var jlink=java.nio.file.Path.of(System.getProperty("java.home"),"bin","jlink");
Map<String,Object> receipt=Map.of("jar_contract_checked",true,"previous_artifact","v1","jlink_tool_present",java.nio.file.Files.isExecutable(jlink),"custom_runtime_built",false,"production_deployed",false);
assert receipt.get("previous_artifact").equals("v1") && receipt.get("custom_runtime_built").equals(false) && receipt.get("production_deployed").equals(false);
```

**Expected:** previousartifactv1 retained;custom_runtime_builtFalse.

**Verify:** Compare the program values or named exception with previousartifactv1 retained;custom_runtime_builtFalse. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
