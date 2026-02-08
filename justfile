# Workflow recipes. Single module list: scripts/modules.

modules := `cat scripts/modules`
act_logs := "act-logs"
dollar := "$"

setup:
    chmod +x scripts/*.sh
    ./scripts/clone-all.sh
    ./scripts/go-work-init.sh
    ./scripts/setup-hooks.sh
    for mod in {{ modules }}; do cp scripts/justfile.module src/$mod/justfile; done

inject-replace:
    ./scripts/inject-go-replace.sh

install-hooks:
    chmod +x scripts/setup-hooks.sh
    ./scripts/setup-hooks.sh

copy-module-justfile:
    for mod in {{ modules }}; do cp scripts/justfile.module src/$mod/justfile; done

bootstrap:
    cd src && go generate ./client/... ./protocol/... ./server/... ./debug-ui/... ./network/...

test-all:
    cd src && go test ./client/... ./protocol/... ./server/... ./debug-ui/... ./network/...

clean:
    rm -rf src

# Run GitHub Actions locally (act). Uses scripts/run_act.py for push main + push tag and logs.
act:
    python3 scripts/run_act.py --log-dir {{ act_logs }}

todo name module:
    python3 scripts/todo_template.py --name "{{name}}" --module "{{module}}"

debug-ui:
    cd src/debug-ui/cmd && go run .
