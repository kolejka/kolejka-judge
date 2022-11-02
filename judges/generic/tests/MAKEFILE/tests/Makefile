.PHONY: all
all: clean environment.zip tools.zip

.PHONY: clean
clean:
	cd environment && make clean ; true
	cd tools && make clean ; true
	rm -rf TESTER environment.zip tools.zip


%.zip:
	cd $* && make clean ; true
	cd $* && zip -9 ../$@ -r .


REAL_JUDGE:=$(shell readlink -f judge.py)
REAL_TESTS:=$(shell readlink -f tests.yaml)
REAL_SOLUTION:=$(shell readlink -f solution.*)

.PHONY: test-local
test-local: all
	rm -rf TESTER ;	mkdir -p TESTER
	curl -s -L https://kolejka.matinf.uj.edu.pl/kolejka-judge -o TESTER/kolejka-judge
	python3 TESTER/kolejka-judge execute --overwrite "$(REAL_JUDGE)" "$(REAL_TESTS)" "$(REAL_SOLUTION)" TESTER/RESULT

.PHONY: test-remote
test-remote: all
	rm -rf TESTER ;	mkdir -p TESTER
	curl -s -L https://kolejka.matinf.uj.edu.pl/kolejka-judge -o TESTER/kolejka-judge
	python3 TESTER/kolejka-judge task "$(REAL_JUDGE)" "$(REAL_TESTS)" "$(REAL_SOLUTION)" TESTER/TASK
	rm TESTER/TASK/kolejka-judge ; ln -s "../kolejka-judge" TESTER/TASK/kolejka-judge
	kolejka-client execute TESTER/TASK TESTER/RESULT
	cat TESTER/RESULT/console_stderr.txt TESTER/RESULT/console_stdout.txt
	echo "Details of the result are in directory TESTER/RESULT"
