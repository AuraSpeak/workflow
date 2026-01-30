.PHONY: setup bootstrap test-all clean

setup:
	chmod +x scripts/clone-all.sh
	chmod +x scripts/go-work-init.sh
	./scripts/clone-all.sh
	./scripts/go-work-init.sh

bootstrap:
	cd src && go generate ./client/... ./protocol/... ./server/... ./debug-ui/... ./network/...

test-all:
	cd src && go test ./client/... ./protocol/... ./server/... ./debug-ui/... ./network/...

clean:
	rm -rf src