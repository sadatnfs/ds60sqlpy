import java.util.*;

public class Main {
    @FunctionalInterface interface FileWork { void run(java.nio.file.Path root) throws Exception; }
    static void withTemp(FileWork work) throws Exception {
        var root=java.nio.file.Files.createTempDirectory("ds60-java-");
        try { work.run(root); }
        finally {
            try(var paths=java.nio.file.Files.walk(root)) {
                for(var path:paths.sorted(Comparator.reverseOrder()).toList()) java.nio.file.Files.deleteIfExists(path);
            }
        }
    }
    public static void main(String[] args) throws Exception {
        // Exercise 1: Round-trip explicit UTF-8
        withTemp(root -> {
            var path = root.resolve("text.txt"); String text = "Café 🙂";
            java.nio.file.Files.writeString(path,text,java.nio.charset.StandardCharsets.UTF_8);
            assert java.nio.file.Files.readString(path,java.nio.charset.StandardCharsets.UTF_8).equals(text);
        });

        // Exercise 2: Distinguish a path from existence
        withTemp(root -> {
            var missing = root.resolve("missing.txt");
            assert missing.getFileName().toString().equals("missing.txt") && !java.nio.file.Files.exists(missing);
        });

        // Exercise 3: Close a directory stream
        withTemp(root -> {
            java.nio.file.Files.writeString(root.resolve("a.txt"),"a"); java.nio.file.Files.writeString(root.resolve("b.txt"),"b");
            try(var entries = java.nio.file.Files.list(root)) { assert entries.count() == 2; }
        });

        // Exercise 4: Request atomic replacement honestly
        withTemp(root -> {
            var target=root.resolve("target.txt"); var staged=root.resolve("staged.txt");
            java.nio.file.Files.writeString(target,"old"); java.nio.file.Files.writeString(staged,"new");
            try {
                java.nio.file.Files.move(staged,target,java.nio.file.StandardCopyOption.ATOMIC_MOVE,java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                assert java.nio.file.Files.readString(target).equals("new") && !java.nio.file.Files.exists(staged);
            } catch(java.nio.file.AtomicMoveNotSupportedException expected) {
                assert java.nio.file.Files.readString(target).equals("old");
            }
        });

        // Exercise 5: Expose a lexical path escape
        withTemp(root -> {
            var candidate=root.resolve("../outside").normalize();
            assert !candidate.startsWith(root.normalize());
        });

        // Exercise 6: Verify cleanup after failure
        final java.nio.file.Path[] created={null}; boolean propagated=false;
        try { withTemp(root -> { created[0]=root; throw new java.io.IOException("fixture failure"); }); }
        catch(java.io.IOException expected) { propagated=expected.getMessage().equals("fixture failure"); }
        assert propagated && created[0]!=null && !java.nio.file.Files.exists(created[0]);
    }
}
