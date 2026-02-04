# Module justfile (copied by "just setup" from workflow repo).
# Use from inside src/<module>. Inject-replace only works when used inside the workflow layout.

# Re-inject local replace directives into go.mod (for local dev after pull).
# Only works when this repo is under a workflow checkout (../../scripts exists).
inject-replace:
    bash -c 'if [ -f ../../scripts/inject-go-replace.sh ]; then ../../scripts/inject-go-replace.sh; else echo "Not in workflow layout (../../scripts not found). Run from workflow root: just inject-replace"; exit 1; fi'
