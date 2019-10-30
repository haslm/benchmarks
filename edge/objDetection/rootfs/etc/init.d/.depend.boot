TARGETS = mountkernfs.sh hostname.sh x11-common mountdevsubfs.sh procps urandom hwclock.sh networking checkroot.sh bootmisc.sh mountnfs-bootclean.sh mountnfs.sh checkroot-bootclean.sh checkfs.sh mountall-bootclean.sh mountall.sh
INTERACTIVE = checkroot.sh checkfs.sh
mountdevsubfs.sh: mountkernfs.sh
procps: mountkernfs.sh
urandom: hwclock.sh
hwclock.sh: mountdevsubfs.sh
networking: procps mountkernfs.sh urandom
checkroot.sh: hwclock.sh mountdevsubfs.sh hostname.sh
bootmisc.sh: mountnfs-bootclean.sh checkroot-bootclean.sh mountall-bootclean.sh
mountnfs-bootclean.sh: mountnfs.sh
mountnfs.sh: networking
checkroot-bootclean.sh: checkroot.sh
checkfs.sh: checkroot.sh
mountall-bootclean.sh: mountall.sh
mountall.sh: checkfs.sh checkroot-bootclean.sh
