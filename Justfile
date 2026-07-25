# ktg-orchestrator Justfile

set shell := ["bash", "-c"]

home := env_var_or_default("HOME", "/tmp")
ai_max_dir := env_var_or_default("AI_MAX_DIR", home / "repos/ai-max")
python := "python3"

build:
    @echo "no local build"

assemble slug *args:
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" assemble {{slug}} {{args}}

status:
    @{{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" status

pull-all:
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" pull-all

ship *args:
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" ship {{args}}

fix-symlinks slug:
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" fix-symlinks {{slug}}

clean *args="":
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" clean {{args}}
