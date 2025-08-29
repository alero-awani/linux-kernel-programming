# Linux Kernel Programming

## Setting up the Environment

### Setup Vagrant

```sh
vagrant up
```

### Update the packages

```sh
sudo apt update
sudo apt install linux-generic-hwe-18.04
sudo reboot
sudo apt install gcc make perl
```

```sh
sudo apt install git fakeroot build-essential tar ncurses-dev tar xz-utils libssl-dev bc stress python3-distutils libelf-dev linux-headers-$(uname -r) bison flex libncurses5-dev util-linux net-tools linux-tools-$(uname -r) exuberant-ctags cscope sysfsutils gnome-system-monitor curl perf-tools-unstable gnuplot rt-tests indent tree pstree smem libnuma-dev numactl hwloc bpfcc-tools sparse flawfinder cppcheck tuna hexdump openjdk-14-jre trace-cmd virt-what 
```

Any Linux system has three required components:

1. BootLoader
2. Operating System (OS) Kernel
3. Root Filesystem

Current Kernel release

```sh
uname -r 
```

### Step 1 – obtaining a Linux kernel source tree

The project uses a very specific Linux kernel version. You will thus download that particular kernel source tree

```sh
mkdir -p ~/Downloads
wget --https-only -O ~/Downloads/linux-5.4.296.tar.xz https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.4.296.tar.xz
```

### Step 2 – extracting the kernel source tree

```sh
mkdir -p Kernels
cd Kernels
tar xf ~/Downloads/linux-5.4.296.tar.xz 
```

As a convenience, and good practice, let's set up an environment variable to point to the location of the root of our kernel source tree:

`export LLKD_KSRC=${HOME}/Kernels/linux-5.4.296`

We extract the kernel source tree into any directory under our home directory (or even elsewhere), unlike in the old days when the tree was always extracted under a root-writeable location (often, /usr/src/). Nowadays, just say no (to that).

How do we know which version exactly of the Linux kernel this code is by just looking at the source? That's easy, one quick way is to just check out the first few lines of the project's Makefile. Incidentally, the kernel uses Makefile's all over the place; most directories have one. We will refer to this Makefile, the one at the root of the kernel source tree, as the top-level Makefile:

```sh
head Makefile
```

### eBPF Program

[Install BCC](https://github.com/iovisor/bcc/blob/master/INSTALL.md#install-build-dependencies-1)

1. Install build dependencies

    ```sh
    sudo apt-get -y install zip bison build-essential cmake flex git libedit-dev \
      libllvm3.9 llvm-3.9-dev libclang-3.9-dev python zlib1g-dev libelf-dev python3-setuptools \
      liblzma-dev arping netperf iperf
    ```

    ```sh
    sudo apt install cmake
    ```

1. Install and compile BCC

    ```sh
    git clone https://github.com/iovisor/bcc.git
    mkdir bcc/build; cd bcc/build
    cmake ..
    make
    sudo make install
    cmake -DPYTHON_CMD=python3 .. # build python3 binding
    pushd src/python/
    make
    sudo make install
    popd
    ```

1. Confirm python

    ```sh
    python3 hello.py
    ```

### Using the localmodconfig approach as a starting point for Kernel Configuration

This is an approach where you base the kernel configuration on the existing (or another) system's kernel modules.

This existing kernel modules-only approach is a good one when the goal is to obtain a starting point for kernel config on an x86-based system by keeping it relatively small and thus make the build quicker as well.

First obtain a snapshot of the currently loaded kernel modules, and then have the kbuild system operate upon it by specifying the localmodconfig target, like so:

```sh
lsmod > /tmp/lsmod.now
cd ${LLKD_KSRC} ; make LSMOD=/tmp/lsmod.now localmodconfig
```

To start over in case of an error

```sh
cd ${LLKD_KSRC} && make mrproper
```

Then run the command before this again. 

```sh
ls -la .config
```

### Configure the Kernel using menuconfig UI

We now have an initial kernel config file (.config) generated for us via the localmodconfig Makefile target, as shown in detail in the previous section, which is a good starting point. Now, we want to further examine and fine-tune our kernel's configuration and we will be using the menuconfig Makefile target.

```sh
make menuconfig
```

- `<*>`: On, feature compiled and built in (compiled in) the
kernel image (y)
- `<M>`: Module, feature compiled and built as a kernel module (an LKM) (m)
- `< >`: Off, not built at all (n)

The kernel configuration is written into a simple ASCII text file in the root of the kernel source tree, named .config. That is, it's saved in `${LLKD_KSRC}/.config`

We will build the kernel (and modules) with these new config options, boot from it, and verify that the preceding kernel config options were set as we wanted.

Every single kernel config option is associated with a config variable of the form `CONFIG_<FOO>`, where `<FOO>`, of course, is replaced with an appropriate name. Internally, these become macros that the build system and indeed the kernel source code uses.

```sh
grep IKCONFIG .config
```

`Caution`: it's best to NOT attempt to edit the .config file manually ("by hand"). There are several inter-dependencies you may not be aware of; always use the kbuild menu system (we suggest via make menuconfig) to edit it.

### Building the Linux Kernel from Source

This includes:
    - building the kernel image and modules
    - installing the kernel modules
    - generating the initramfs image and bootloader setup (Understanding the initramfs framework)
    - customizing the GRUB bootloader
    - Verifying our new kernel's configuration

1. Run the command `make help` to see all possible make targets.

    - `vmlinux` is the uncompressed kernel image (it can be large)
    - The `modules` target implies that all kernel config options marked as m (for module) will be built as kernel modules.
    - `bzImage` is architecture-specific. On an x86[-64] system, this is the name of the compressed kernel image – the one the bootloader will actually load into RAM, uncompress in memory, and boot into; in effect, the kernel image file.

1. Ensure you're in the root of the configured kernel source tree and type `make`.