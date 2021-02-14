#!/usr/bin/python

# demo.py

import time
import nvtx

@nvtx.annotate(color="blue")
def my_function_3rd():
    time.sleep(2)

@nvtx.annotate(color="blue")
def my_function_2nd():
    time.sleep(1)
    my_function_3rd()

@nvtx.annotate(color="blue")
def my_function():
    for i in range(5):
        with nvtx.annotate("my_loop", color="red"):
            time.sleep(max(0, i + 2))
    my_function_2nd()

my_function()
