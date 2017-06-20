#!/usr/bin/env bash
ansible-playbook devenv-playbook.yml
v/bin/python scripts/stage1.py
v/bin/python scripts/stage2.py
v/bin/python scripts/stage3.py
v/bin/python scripts/stage4.py
v/bin/python scripts/stage5.py