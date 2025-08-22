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

`export LLKD_KSRC=${HOME}/kernels/linux-5.4.296`

We extract the kernel source tree into any directory under our home directory (or even elsewhere), unlike in the old days when the tree was always extracted under a root-writeable location (often, /usr/src/). Nowadays, just say no (to that).

How do we know which version exactly of the Linux kernel this code is by just looking at the source? That's easy, one quick way is to just check out the first few lines of the project's Makefile. Incidentally, the kernel uses Makefile's all over the place; most directories have one. We will refer to this Makefile, the one at the root of the kernel source tree, as the top-level Makefile:

```sh
head Makefile
```
