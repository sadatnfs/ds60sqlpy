import java.util.*;

public class Main {
    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.TYPE)
    public @interface Version { int value(); }
    public interface Greeting { String greet(String name); }
    @Version(2) public static final class Friendly implements Greeting {
        public Friendly(){}
        public String greet(String name){if(name==null||name.isBlank())throw new IllegalArgumentException("nonblank name required");return "Hello, "+name;}
    }
    static final class ServiceFixture implements AutoCloseable {
        final java.nio.file.Path root;final java.net.URLClassLoader loader;
        ServiceFixture() throws Exception {root=java.nio.file.Files.createTempDirectory("ds60-service-");var descriptor=root.resolve("META-INF/services").resolve(Greeting.class.getName());java.nio.file.Files.createDirectories(descriptor.getParent());java.nio.file.Files.writeString(descriptor,Friendly.class.getName()+System.lineSeparator());loader=new java.net.URLClassLoader(new java.net.URL[]{root.toUri().toURL()},Main.class.getClassLoader());}
        public void close() throws Exception {loader.close();try(var paths=java.nio.file.Files.walk(root)){for(var path:paths.sorted(Comparator.reverseOrder()).toList())java.nio.file.Files.deleteIfExists(path);}}
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Inspect a retained annotation
        Version version=Friendly.class.getAnnotation(Version.class);
        assert version!=null && version.value()==2;

        // Exercise 2: Invoke a known public method reflectively
        var method=Friendly.class.getMethod("greet",String.class);
        assert method.invoke(new Friendly(),"Ada").equals("Hello, Ada");

        // Exercise 3: Load a real local service descriptor
        try(ServiceFixture fixture=new ServiceFixture()) {
            var providers=java.util.ServiceLoader.load(Greeting.class,fixture.loader).stream().map(java.util.ServiceLoader.Provider::get).toList();
            assert providers.size()==1 && providers.get(0).getClass()==Friendly.class;
            assert providers.get(0).greet("Lin").equals("Hello, Lin");
        }

        // Exercise 4: Preserve a reflected target failure
        boolean targetFailure=false;
        try{method.invoke(new Friendly()," ");}catch(java.lang.reflect.InvocationTargetException expected){targetFailure=expected.getCause() instanceof IllegalArgumentException;}
        assert targetFailure;

        // Exercise 5: Reject missing class andmethod contracts
        boolean missingClass=false,missingMethod=false;
        try{Class.forName("course.missing.NoSuchProvider");}catch(ClassNotFoundException expected){missingClass=true;}
        try{Friendly.class.getMethod("greet",int.class);}catch(NoSuchMethodException expected){missingMethod=true;}
        assert missingClass && missingMethod;

        // Exercise 6: Treat provider metadata as a policy input
        int supportedMaximum=2;assert version.value()>=1 && version.value()<=supportedMaximum;
        assert 3>supportedMaximum;
    }
}
