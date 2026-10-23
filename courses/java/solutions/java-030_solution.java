import java.util.*;

public class Main {
    record Account(String id,long cents,String note){Account{if(id==null||!id.matches("[A-Za-z0-9_-]{1,32}")||cents<0||note==null)throw new IllegalArgumentException("invalid account");}}
    static byte[] encode(Account value,int version) throws java.io.IOException {
        if(version!=1&&version!=2)throw new java.io.IOException("unsupported version");var bytes=new java.io.ByteArrayOutputStream();
        try(var out=new java.io.DataOutputStream(bytes)){out.writeInt(0x44533630);out.writeShort(version);writeText(out,value.id(),64);out.writeLong(value.cents());if(version==2)writeText(out,value.note(),128);}
        return bytes.toByteArray();
    }
    static void writeText(java.io.DataOutputStream out,String value,int limit) throws java.io.IOException {if(value.length()>limit)throw new java.io.IOException("text length limit");var encoded=java.nio.charset.StandardCharsets.UTF_8.newEncoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT).onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT).encode(java.nio.CharBuffer.wrap(value));byte[] bytes=new byte[encoded.remaining()];encoded.get(bytes);if(bytes.length>limit)throw new java.io.IOException("text length limit");out.writeInt(bytes.length);out.write(bytes);}
    static String readText(java.io.DataInputStream input,int limit) throws java.io.IOException {int length=input.readInt();if(length<0||length>limit)throw new java.io.IOException("text length limit");byte[] bytes=input.readNBytes(length);if(bytes.length!=length)throw new java.io.EOFException("truncated text");return java.nio.charset.StandardCharsets.UTF_8.newDecoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT).onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT).decode(java.nio.ByteBuffer.wrap(bytes)).toString();}
    static Account decode(byte[] bytes) throws java.io.IOException {
        try(var input=new java.io.DataInputStream(new java.io.ByteArrayInputStream(bytes))){if(input.readInt()!=0x44533630)throw new java.io.IOException("magic mismatch");int version=input.readUnsignedShort();if(version!=1&&version!=2)throw new java.io.IOException("unsupported version");String id=readText(input,64);long cents=input.readLong();String note=version==2?readText(input,128):"unlabelled";if(input.read()!=-1)throw new java.io.IOException("trailing bytes");try{return new Account(id,cents,note);}catch(IllegalArgumentException error){throw new java.io.IOException("invalid domain record",error);}}
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Round-trip version2 data
        Account record=new Account("a1",125,"Café");byte[] encoded=encode(record,2);
        assert decode(encoded).equals(record);

        // Exercise 2: Apply a version1 default
        Account legacy=decode(encode(new Account("a1",125,"ignored by v1"),1));
        assert legacy.id().equals("a1") && legacy.cents()==125 && legacy.note().equals("unlabelled");

        // Exercise 3: Reject an unknown version
        byte[] unknown=encoded.clone();unknown[4]=0;unknown[5]=99;boolean rejected=false;
        try{decode(unknown);}catch(java.io.IOException expected){rejected=expected.getMessage().contains("version");}
        assert rejected;

        // Exercise 4: Detect truncation
        boolean truncated=false;
        try{decode(Arrays.copyOf(encoded,encoded.length-1));}catch(java.io.IOException expected){truncated=true;}
        assert truncated;

        // Exercise 5: Reject an oversized declared text length
        byte[] huge=encoded.clone();java.nio.ByteBuffer.wrap(huge,6,4).putInt(Integer.MAX_VALUE);boolean bounded=false;
        try{decode(huge);}catch(java.io.IOException expected){bounded=expected.getMessage().contains("length");}
        assert bounded;

        // Exercise 6: Reject trailing data andinvalid domain state
        byte[] trailing=Arrays.copyOf(encoded,encoded.length+1);boolean extra=false,negative=false;
        try{decode(trailing);}catch(java.io.IOException expected){extra=expected.getMessage().contains("trailing");}
        try{new Account("a1",-1,"x");}catch(IllegalArgumentException expected){negative=true;}
        assert extra && negative;
    }
}
