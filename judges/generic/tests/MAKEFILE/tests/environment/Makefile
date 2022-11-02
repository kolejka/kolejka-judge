BUILD_OFFICE:=$(subst \,/,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

.PHONY: all
all: exec_script

.PHONY: clean
clean:
	rm -rf exec_script bin src/obj/Release src/Solution.cs

.PHONY: prepare
prepare:
	true

.PHONY: build
build: prepare
	DOTNET_CLI_HOME="$(BUILD_OFFICE)" DOTNET_CLI_TELEMETRY_OPTOUT=1 dotnet build --no-restore src/Solution.csproj -c Release -o bin -nologo -clp:NoSummary

exec_script: build
	echo '#/bin/bash' > $@
	echo 'OFFICE="$$(dirname "$$(readlink -f "$$(which "$${0}")")")"' >> $@
	echo 'exec dotnet "$${OFFICE}/bin/Solution.dll"' >> $@
	chmod 755 $@
