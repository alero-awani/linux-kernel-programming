from bcc import BPF

program = """
int hello(void *ctx) {
    bpf_trace_printk("Hello from execve, this is Alero checking up on you!\\n");
    return 0;
}
"""

b = BPF(text=program)
b.attach_kprobe(event="__x64_sys_execve", fn_name="hello")

print("Tracing execve syscalls... Ctrl-C to exit.")
b.trace_print()                