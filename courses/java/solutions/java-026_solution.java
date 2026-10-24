import java.util.*;

public class Main {
    static final class ModuleFixture implements AutoCloseable {
        final java.nio.file.Path root,source,output;String diagnostics="";
        ModuleFixture() throws Exception {
            root=java.nio.file.Files.createTempDirectory("ds60-modules-");source=root.resolve("src");output=root.resolve("out");
            write("course.greeting/module-info.java","module course.greeting { exports edu.example.greeting; }");
            write("course.greeting/edu/example/greeting/Greeter.java","package edu.example.greeting; public final class Greeter { public static String message(){return \"Hello, modules!\";} }");
            write("course.app/module-info.java","module course.app { requires course.greeting; }");
            write("course.app/edu/example/app/Main.java","package edu.example.app; public class Main { public static void main(String[] args){System.out.println(edu.example.greeting.Greeter.message());} }");
        }
        void write(String relative,String text) throws Exception {var path=source.resolve(relative);java.nio.file.Files.createDirectories(path.getParent());java.nio.file.Files.writeString(path,text);}
        int compile(){var compiler=javax.tools.ToolProvider.getSystemJavaCompiler();if(compiler==null)throw new IllegalStateException("JDK compiler required");var errors=new java.io.ByteArrayOutputStream();int code=compiler.run(null,errors,errors,"--release","21","--module-source-path",source.toString(),"-d",output.toString(),"-m","course.greeting,course.app");diagnostics=errors.toString(java.nio.charset.StandardCharsets.UTF_8);return code;}
        String childStderr="";
        String run() throws Exception {
            String executable=java.nio.file.Path.of(System.getProperty("java.home"),"bin","java").toString();
            var stdout=root.resolve("child.stdout");var stderr=root.resolve("child.stderr");
            var process=new ProcessBuilder(executable,"-ea","--module-path",output.toString(),"-m","course.app/edu.example.app.Main").redirectOutput(stdout.toFile()).redirectError(stderr.toFile()).start();
            if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)){process.destroyForcibly();throw new AssertionError("child JVM timeout");}
            String text=java.nio.file.Files.readString(stdout);childStderr=java.nio.file.Files.readString(stderr);
            if(process.exitValue()!=0)throw new AssertionError("child exit "+process.exitValue()+": "+childStderr);
            return text;
        }
        public void close() throws java.io.IOException {try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Inspect a platform module
        assert String.class.getModule().getName().equals("java.base");assert String.class.getPackageName().equals("java.lang");

        // Exercise 2: Inspect the classroom classpath context
        assert !Main.class.getModule().isNamed();

        // Exercise 3: Compile two real modules
        try(ModuleFixture fixture=new ModuleFixture()) {
            assert fixture.compile()==0;
            assert java.nio.file.Files.isRegularFile(fixture.output.resolve("course.greeting/module-info.class"));
            assert java.nio.file.Files.isRegularFile(fixture.output.resolve("course.app/module-info.class"));
        }

        // Exercise 4: Inspect declared dependencies andexports
        try(ModuleFixture fixture=new ModuleFixture()) {
            assert fixture.compile()==0;var finder=java.lang.module.ModuleFinder.of(fixture.output);
            var app=finder.find("course.app").orElseThrow().descriptor();var library=finder.find("course.greeting").orElseThrow().descriptor();
            assert app.requires().stream().anyMatch(item -> item.name().equals("course.greeting"));
            assert library.exports().stream().anyMatch(item -> item.source().equals("edu.example.greeting"));
        }

        // Exercise 5: Run the modular application
        try(ModuleFixture fixture=new ModuleFixture()) {
            assert fixture.compile()==0;assert fixture.run().strip().equals("Hello, modules!");
        }

        // Exercise 6: Reject a missing module dependency
        try(ModuleFixture fixture=new ModuleFixture()) {
            java.nio.file.Files.writeString(fixture.source.resolve("course.app/module-info.java"),"module course.app { requires course.missing; }");
            assert fixture.compile()!=0 && !fixture.diagnostics.isBlank();
        }
    }
}
