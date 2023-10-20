#!/usr/bin/env python3


import os
import sys
import pathlib

src_name = sys.argv[1]

lines = sys.stdin.readlines()


def pop_sha1():
    sha1_file = pathlib.PosixPath("/tmp/change_sha1.txt")
    sha1_list = sha1_file.read_text().rstrip().split("\n")
    sha1_file.write_text("\n".join(sha1_list[:-1]))
    return sha1_list[-1]


sys.stdout.write("[promoted]")
for l in lines:
    sys.stdout.write(l)

print(
    f"\n\nThis commit was initially merged in https://github.com/ansible-collections/{src_name}"
)
print(f"See: https://github.com/ansible-collections/{src_name}/commit/{pop_sha1()}")
