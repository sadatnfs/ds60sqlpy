# java-030: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Serialization turns domain values into a representation that another process orversion can read. A format needs an explicit schema,version,encoding andsize policy. A reader should validate before allocating large buffers orconstructing trusted domain objects. Schema evolution is a compatibility decision:an older version may omit a newly added field,which needs a documented default orupgrade rule. Unknown versions should not be guessed at silently.

This lesson defines a small explicit binary format using DataInputStream andDataOutputStream. It deliberately avoids Java object deserialization for untrusted input. The format has a magic number,a version,bounded UTF-8 text,integer cents andan optional version2 note. A version1 record receives a declared default note. The decoder rejects invalid lengths,malformed UTF-8,truncation,trailing bytes anddomain violations. These checks make the data boundary visible rather than relying on a class name to imply trust.

**Wire schema:** The field order,types,encoding andversion of serialized data.

**Schema evolution:** A declared compatibility policy between format versions.

**Length bound:** A maximum accepted size checked before allocation.

**Deserialization boundary:** Validation required before external bytes become trusted objects.

## Reading the reference

Write a fixed magicint andversion number before fields. Text is UTF-8 bytes preceded by a bounded integer length. Read thelength,validate it,then read exactly thatmany bytes. A CharsetDecoder withREPORT rejects malformed sequences instead of replacing them. The domain record validates nonnegative cents andidentifier shape. Version2 adds a note;version1 decodes with the explicit defaultunlabelled.

## Exercise 1: Round-trip version2 data

Task: Encode accounta1,balance125,noteCafé withversion2 anddecode.

The comparison includes both domain values andtext identity. A successful bytewrite alone would not show that the reader agrees onencoding andfield order.

```java
Account record=new Account("a1",125,"Café");byte[] encoded=encode(record,2);
assert decode(encoded).equals(record);
```

**Expected:** equal domain record andexact Unicode note.

**Verify:** Compare the program values or named exception with equal domain record andexact Unicode note. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Apply a version1 default

Task: Encode the same core fields usingversion1,which lacksnote.

The default is an explicit compatibility rule. It should not be inferred from an emptyString orwhatever value happened to initialize a field.

```java
Account legacy=decode(encode(new Account("a1",125,"ignored by v1"),1));
assert legacy.id().equals("a1") && legacy.cents()==125 && legacy.note().equals("unlabelled");
```

**Expected:** decoded noteunlabelled.

**Verify:** Compare the program values or named exception with decoded noteunlabelled. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Reject an unknown version

Task: Change theversion bytes to99 anddecode.

A reader that guesses the layout of an unknown version can reinterpret bytes incorrectly while appearing to succeed.

```java
byte[] unknown=encoded.clone();unknown[4]=0;unknown[5]=99;boolean rejected=false;
try{decode(unknown);}catch(java.io.IOException expected){rejected=expected.getMessage().contains("version");}
assert rejected;
```

**Expected:** IOException namingversion.

**Verify:** Compare the program values or named exception with IOException namingversion. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Detect truncation

Task: Remove thefinalbyte from a validversion2payload.

The reader must obtain exactly the declared fieldlength. A partial field is not a valid shorter value.

```java
boolean truncated=false;
try{decode(Arrays.copyOf(encoded,encoded.length-1));}catch(java.io.IOException expected){truncated=true;}
assert truncated;
```

**Expected:** IOException orEOFException before returning a record.

**Verify:** Compare the program values or named exception with IOException orEOFException before returning a record. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject an oversized declared text length

Task: Replace thefirsttextlength withInteger.MAX_VALUE.

Length-prefix validation is a resource boundary. Reading orallocating first andchecking afterward defeats that protection.

```java
byte[] huge=encoded.clone();java.nio.ByteBuffer.wrap(huge,6,4).putInt(Integer.MAX_VALUE);boolean bounded=false;
try{decode(huge);}catch(java.io.IOException expected){bounded=expected.getMessage().contains("length");}
assert bounded;
```

**Expected:** IOException forlength before allocating thatsize.

**Verify:** Compare the program values or named exception with IOException forlength before allocating thatsize. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject trailing data andinvalid domain state

Task: Append anextra byte,then try constructing a negative-balance account.

Format validity anddomain validity are separate gates. The fixture chooses strict trailing-byte rejection rather than an undocumented forward-compatibility policy.

```java
byte[] trailing=Arrays.copyOf(encoded,encoded.length+1);boolean extra=false,negative=false;
try{decode(trailing);}catch(java.io.IOException expected){extra=expected.getMessage().contains("trailing");}
try{new Account("a1",-1,"x");}catch(IllegalArgumentException expected){negative=true;}
assert extra && negative;
```

**Expected:** trailing payloadIOException;negative balanceIllegalArgumentException.

**Verify:** Compare the program values or named exception with trailing payloadIOException;negative balanceIllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
