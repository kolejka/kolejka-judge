import pkg.test.RandomName;

public class Main {
    public static void main(String[] args) {
        RandomName cls = new RandomName();
        if(new Dependency().method() == 4) {
            cls.method();
        }
    }
}
