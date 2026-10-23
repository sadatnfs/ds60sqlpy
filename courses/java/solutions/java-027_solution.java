import java.util.*;

public class Main {
    static final class BuildFixture implements AutoCloseable {
        final java.nio.file.Path root,source,classes;
        BuildFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-build-");source=root.resolve("Hello.java");classes=root.resolve("classes");java.nio.file.Files.createDirectories(classes);java.nio.file.Files.writeString(source,"public class Hello { public static void main(String[] args){System.out.println(\"build-ok\");} }");}
        int compile(){var compiler=javax.tools.ToolProvider.getSystemJavaCompiler();if(compiler==null)throw new IllegalStateException("JDK required");return compiler.run(null,null,null,"--release","21","-d",classes.toString(),source.toString());}
        java.nio.file.Path pack(String name) throws Exception {var target=root.resolve(name);var jar=java.util.spi.ToolProvider.findFirst("jar").orElseThrow();var output=new java.io.StringWriter();int result=jar.run(new java.io.PrintWriter(output),new java.io.PrintWriter(output),"--create","--file",target.toString(),"--main-class","Hello","--date=2020-01-01T00:00:02Z","-C",classes.toString(),".");if(result!=0)throw new AssertionError(output.toString());return target;}
        String run(java.nio.file.Path jar) throws Exception {String executable=java.nio.file.Path.of(System.getProperty("java.home"),"bin","java").toString();var process=new ProcessBuilder(executable,"-ea","-jar",jar.toString()).redirectErrorStream(true).start();if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)){process.destroyForcibly();throw new AssertionError("JAR timeout");}String output=new String(process.getInputStream().readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);if(process.exitValue()!=0)throw new AssertionError(output);return output;}
        public void close() throws Exception {try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Compile a literal application
        try(BuildFixture fixture=new BuildFixture()) {assert fixture.compile()==0;assert java.nio.file.Files.isRegularFile(fixture.classes.resolve("Hello.class"));}

        // Exercise 2: Create a runnable archive
        try(BuildFixture fixture=new BuildFixture()) {
            assert fixture.compile()==0;var jar=fixture.pack("one.jar");
            try(var archive=new java.util.jar.JarFile(jar.toFile())){assert archive.getJarEntry("Hello.class")!=null;assert archive.getManifest().getMainAttributes().getValue("Main-Class").equals("Hello");}
        }

        // Exercise 3: Compare two builds with fixed metadata
        try(BuildFixture fixture=new BuildFixture()) {
            assert fixture.compile()==0;var a=fixture.pack("a.jar");var b=fixture.pack("b.jar");
            assert Arrays.equals(java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(a)),java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(b)));
        }

        // Exercise 4: Execute the packaged entrypoint
        try(BuildFixture fixture=new BuildFixture()) {assert fixture.compile()==0;assert fixture.run(fixture.pack("run.jar")).strip().equals("build-ok");}

        // Exercise 5: Detect a changed source identity
        var digest=java.security.MessageDigest.getInstance("SHA-256");
        byte[] first=digest.digest("class A { int x=1; }".getBytes(java.nio.charset.StandardCharsets.UTF_8));
        byte[] second=digest.digest("class A { int x=2; }".getBytes(java.nio.charset.StandardCharsets.UTF_8));
        assert !Arrays.equals(first,second);

        // Exercise 6: Record an explicit dependency contract
        Map<String,String> dependency=Map.of("coordinate","com.h2database:h2","version","2.5.252","hash_policy","verify prepared artifact SHA256");
        assert dependency.get("version").equals("2.5.252") && !dependency.get("version").equals("LATEST");
    }
}
