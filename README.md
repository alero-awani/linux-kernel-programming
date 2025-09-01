# Linux Kernel Programming

## References

- [Linux Kernel Programming by Kaiwan N. Billimoria](https://www.oreilly.com/library/view/linux-kernel-programming/9781789953435/)
- [Learning eBPF by Liz Rice](https://www.oreilly.com/library/view/learning-ebpf/9781098135119/)

## Table of Contents

1. [Setting up the Environment](#setting-up-the-environment)
   - [Setup Vagrant](#setup-vagrant)
   - [Update the packages](#update-the-packages)
2. [Kernel Source Tree](#kernel-source-tree)
   - [Step 1 obtaining a Linux kernel source tree](#step-1-obtaining-a-linux-kernel-source-tree)
   - [Step 2 extracting the kernel source tree](#step-2-extracting-the-kernel-source-tree)
3. [Kernel Configuration](#using-the-localmodconfig-approach-as-a-starting-point-for-kernel-configuration)
   - [Using the localmodconfig approach](#using-the-localmodconfig-approach-as-a-starting-point-for-kernel-configuration)
   - [Configure the Kernel using menuconfig UI](#configure-the-kernel-using-menuconfig-ui)
4. [Building the Linux Kernel from Source](#building-the-linux-kernel-from-source)
   - [STEP 1: Building the Kernel Image and Modules](#step-1-building-the-kernel-image-and-modules)
   - [STEP 2: Installing the Kernel Modules](#step-2-installing-the-kernel-modules)
   - [STEP 3: Generating the initramfs image and bootloader setup](#step-3-generating-the-initramfs-image-and-bootloader-setup)
   - [Understanding the initramfs framework](#understanding-the-initramfs-framework)
5. [eBPF Program](#ebpf-program)

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

## Kernel Source Tree

### Step 1 obtaining a Linux kernel source tree

The project uses a very specific Linux kernel version. You will thus download that particular kernel source tree

```sh
mkdir -p ~/Downloads
wget --https-only -O ~/Downloads/linux-5.4.296.tar.xz https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.4.296.tar.xz
```

### Step 2 extracting the kernel source tree

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

Note: `kbuild` is the kernel’s build system — essentially a specialized framework of Makefiles and scripts that automates compiling, linking, and packaging the kernel and its modules.

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

### STEP 1: Building the Kernel Image and Modules

1. Run the command `make help` to see all possible make targets.

    - `vmlinux` is the uncompressed kernel image (it can be large)
    - The `modules` target implies that all kernel config options marked as m (for module) will be built as kernel modules.
    - `bzImage` is architecture-specific. On an x86[-64] system, this is the name of the compressed kernel image – the one the bootloader will actually load into RAM, uncompress in memory, and boot into; in effect, the kernel image file.

1. Ensure you're in the root of the configured kernel source tree and type `make`.

1. By the time this step terminates, three key files (among many) have been generated by the kbuild system.
In the root of the kernel source tree, we have the following:
    - The uncompressed kernel image file, `vmlinux` (only for debugging).
    - The symbol-address mapping file, `System.map`
    - The compressed bootable kernel image file, `bzImage`

1. Let's check them out.

    ```sh
    ls -lh vmlinux System.map
    ```

1. The actual kernel image file that the bootloader loads up and boots into will always be in the generic location of `arch/<arch>/boot/`; hence, for the x86 architecture, we have the following:

    ```sh
    ls -l arch/x86/boot/bzImage
    file arch/x86/boot/bzImage
    ```

    ```sh
    #output
    vagrant@ubuntu-bionic:~/Kernels/linux-5.4.296$ file arch/x86/boot/bzImage
    arch/x86/boot/bzImage: Linux kernel x86 boot executable bzImage, version 5.4.296llkd01 (vagrant@ubuntu-bionic) #2 SMP Fri Aug 29 17:06:51 UTC 2025, RO-rootFS, swap_dev 0x8, Normal VGA
    ```

1. Our kernel image and modules are ready. In the next step we will do the actual installation.

### STEP 2: Installing the Kernel Modules

All the kernel config options that were marked as m have actually now been built. As you shall learn, that's not quite enough: they must now be installed into a known location on the system i.e within the root filesystem so that, at boot, the system can actually find and load them into kernel memory.

1. To see the kernel modules just generated by the previous step. Note: kernel modules are stored as (.ko files)

    ```sh
    find . -name "*.ko"

    find . -name "*.ko" -ls | egrep -i "vbox|msdos|uio" 
    ```

1. Features have been asked to be built as modules will not be encoded within the vmlinux or bzImage kernel image files. They will exist as standalone (well, kind of) kernel modules.

1. The "well-known location within the root filesystem" where we need to install the the binary kernel modules is `/lib/modules/$(uname - r)/`, where $(uname -r) yields the kernel version number, of course.

1. Invoke the `modules_install` Makefile target.

    ```sh
    sudo make modules_install
    ```

1. The result of the module installation step:

    ```sh
    ls /lib/modules/

    # output
    5.4.0-150-generic  5.4.296llkd01
    ```

    For each (Linux) kernel we can boot the system into, there is a folder under /lib/modules/, whose name is the kernel release, as expected.

1. Let's look into the installed modules

    ```sh
    ls /lib/modules/5.4.296llkd01/kernel/

    find /lib/modules/5.4.296llkd01/ -name "*.ko" | egrep "vboxguest|msdos|uio"
    ```
  
    The next step is to generate the so-called initramfs (or initrd) image and set up the bootloader.

### STEP 3: Generating the initramfs image and bootloader setup

1. Generate the initramfs (short for initial ram filesystem) image file as well as update the bootloader.

    ```sh
    sudo make install
    ```

So what happens at this step:

- An `install.sh` script copies the following files into the `/boot` folder
  - config-5.4.296llkd01
  - System.map-5.4.296llkd01
  - initrd.img-5.4.296llkd01
  - vmlinuz-5.4.296llkd01
- The `initramfs` image is built as well, Once built, the initramfs image is also copied into the `/boot` directory.
- The file named `vmlinuz-<kernel-ver>` is a copy of the arch/x86/boot/bzImage file
- The GRUB bootloader configuration file located at /boot/grub/grub.cfg is updated to reflect the fact that a new kernel is now available for boot.

    It is the compressed kernel image – the image file that the bootloader will be configured to load into RAM, uncompress, and jump to its entry point, thus handing over control to the kernel!

A brand new 5.4 kernel, along with all requested kernel modules and the initramfs image, have been generated, and the (GRUB) bootloader has been updated. All that remains is to reboot the system, select the new kernel image on boot (from the bootloader menu screen), boot up, log in, and verify that all is okay.

### Understanding the initramfs framework

What exactly is this initramfs or initrd image ?

The config directive for this is called `CONFIG_BLK_DEV_INITRD`

The initramfs framework is essentially a kind of **middle-man** between the early kernel boot and usermode. It allows us to run user space applications (or scripts) before the actual root filesystem has been mounted i.e it allows us to run user mode apps that the kernel cannot normally run during boot time.

It allows us to do the following and many more:

- Accept a password (for encrypted disks)
- Load up kernel modules as required

```sh
lsinitramfs /boot/initrd.img-5.4.296llkd01
```

### STEP 4: Customizing the GRUB bootloader

5.4.0-150-generic

"Advanced options for Ubuntu>Ubuntu, with Linux 5.4.0-150-generic"


/boot/grub/mybackground.png