# Workflow recipes (replaces Makefile)

setup:
    chmod +x scripts/clone-all.sh scripts/go-work-init.sh
    ./scripts/clone-all.sh
    ./scripts/go-work-init.sh

bootstrap:
    cd src && go generate ./client/... ./protocol/... ./server/... ./debug-ui/... ./network/...

test-all:
    cd src && go test ./client/... ./protocol/... ./server/... ./debug-ui/... ./network/...

clean:
    rm -rf src

todo name module:
    python3 scripts/todo_template.py --name "{{name}}" --module "{{module}}"
