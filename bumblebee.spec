# Package should be built in nonfree only, as it only provides features for nvidia-current

%define snap 20170102

Name:		bumblebee
Version:	3.2.1
Release:	3.%{snap}.1
Summary:	Daemon managing Nvidia Optimus hybrid graphics cards
Group:		System/Kernel and hardware
License:	GPLv3+
URL:		https://github.com/Bumblebee-Project/bumblebee
# git clone -b develop https://github.com/Bumblebee-Project/Bumblebee.git
# git archive -o bumblebee-3.2.1-`date +%Y%m%d`.tar --prefix=bumblebee-3.2.1/ develop ; xz -9e bumblebee-3.2.1-`date +%Y%m%d`.tar
Source0:	%{name}-%{version}-%{snap}.tar.xz
BuildRequires:	help2man
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(libbsd)
BuildRequires:	pkgconfig(libkmod)
Requires(pre):	rpm-helper
Requires(pre):	update-alternatives
Requires:	kmod(bbswitch.ko)
Requires:	%{name}-bin
Excludearch:	%{armx}
# VirtualGl is the default bridge for upstream, the alternative being primus
# As of now (3.2.1-5) primus shows better performances and compability, so we use it as default
Suggests:     VirtualGL
Suggests:     %mklibname VirtualGL

# Files were moved
Conflicts:      %{name}-nvidia < 3.2.1-3

%description
Bumblebee is an effort to make NVIDIA Optimus enabled laptops work in
GNU/Linux systems. These laptops are built in such a way that the NVIDIA
graphics card can be used on demand so that battery life is improved and
temperature is kept low.

It disables the discrete graphics card if no client is detected, and start
an X server making use of NVIDIA card if requested then let software GL
implementations (such as VirtualGL or primus) copy frames to the visible
display that runs on the integrated graphics.

This package only provides features for using the proprietary nvidia drivers.
Users of the libre nouveau driver should prefer using DRI PRIME over
Bumblebee: https://nouveau.freedesktop.org/wiki/Optimus

%files
%doc README.install.urpmi README.markdown doc/RELEASE_NOTES_3_2_1
%{_sysconfdir}/bash_completion.d/optirun
%{_sysconfdir}/modprobe.d/%{name}.conf
%dir %{_sysconfdir}/bumblebee/
%dir %{_sysconfdir}/bumblebee/xorg.conf.d
%config(noreplace) %{_sysconfdir}/bumblebee/xorg.conf.nouveau
%config(noreplace) %{_sysconfdir}/bumblebee/xorg.conf.nvidia
%config(noreplace) %{_sysconfdir}/bumblebee/xorg.conf.d/10-dummy.conf
%{_udevrulesdir}/99-bumblebee-nvidia-dev.rules
%{_systemunitdir}/bumblebeed.service
%{_presetdir}/86-bumblebee.preset
%{_sbindir}/bumblebeed
%{_bindir}/bumblebee-bugreport
%{_bindir}/optirun
%{_mandir}/man1/bumblebeed.1.*
%{_mandir}/man1/optirun.1.*

%pre
%_pre_groupadd %{name}
if [ "$1" -eq "1" ]; then
    users=$(getent passwd | awk -F: '$3 >= 500 && $3 < 60000 {print $1}')
    for user in $users; do
	gpasswd -a $user bumblebee
    done
    /usr/sbin/update-alternatives --set gl_conf %{_sysconfdir}/ld.so.conf.d/GL/standard.conf
fi

%post
# simplew: still needs this since in release 3 services were not set
# enabled and seams that still isnt properly handeled in %%_post_service
if [ "$1" -ge "1" ]; then
# Enable (but don't start) the unit by default
    /bin/systemctl enable bumblebeed.service
# Start bumblebeed service
    /bin/systemctl start bumblebeed.service
fi

%postun
# We need this since "%%_postun_groupdel %%{name}" doesnt remove the group if
# set to a user
if [ "$1" -eq "0" ];then
    /usr/sbin/groupdel bumblebee
fi

#--------------------------------------------------------------------

%package nvidia
Summary:	Bumblebee configuration files and binaries for nvidia-current driver
Group:		System/Kernel and hardware
Requires:	%{name} = %{EVRD}
Requires:	x11-driver-video-nvidia-current
Requires:	primus-nvidia
Obsoletes:	%{name}-nouveau < 3.2.1-3
Provides:	%{name}-bin = %{EVRD}

%description nvidia
Bumblebee configuration files and binaries built against
the nvidia-current driver.

%files nvidia
%config(noreplace) %{_sysconfdir}/bumblebee/bumblebee.conf
%{_bindir}/nvidia-settings-bumblebee

#--------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}

%build
autoreconf -vfi

%configure \
    --with-udev-rules=%{_udevrulesdir} \
    CONF_BRIDGE=primus \
    CONF_DRIVER=nvidia \
    CONF_DRIVER_MODULE_NVIDIA=nvidia-current \
%ifarch x86_64
    CONF_LDPATH_NVIDIA=%{_libdir}/nvidia-current:%{_usr}/lib/nvidia-current \
    CONF_MODPATH_NVIDIA=%{_libdir}/nvidia-current/xorg,%{_usr}/lib/nvidia-current/xorg,%{_libdir}/xorg/modules,%{_usr}/lib/xorg/modules \
    CONF_PRIMUS_LD_PATH=%{_libdir}/primus:%{_usr}/lib/primus
%else
    CONF_LDPATH_NVIDIA=%{_libdir}/nvidia-current \
    CONF_MODPATH_NVIDIA=%{_libdir}/nvidia-current/xorg,%{_libdir}/xorg/modules \
    CONF_PRIMUS_LD_PATH=%{_libdir}/primus
%endif

%make

%install
%makeinstall_std
install -D -m644 scripts/systemd/bumblebeed.service %{buildroot}%{_systemunitdir}/bumblebeed.service

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-bumblebee.preset << EOF
enable bumblebeed.service
EOF

install -d %{buildroot}%{_sysconfdir}/modprobe.d
cat << EOF > %{buildroot}%{_sysconfdir}/modprobe.d/%{name}.conf
blacklist nvidia-current
blacklist nouveau

# Map removal of modules to correct command
# This allows modprobe -r nvidia to work
remove nvidia rmmod nvidia

# Needed for bumblebee as it tries to remove nvidia-current, which is the module
# load name. The driver is still "nvidia" once loaded, thus the removal fails.
remove nvidia-current rmmod nvidia

# Switch card off when booting, on when unloading bbswitch (shutdown)
options bbswitch load_state=0 unload_state=1
EOF

# Tell users to add themselves to the bumblebee group on new installs
cat << EOF > README.install.urpmi

To be able to use bumblebee via the 'optirun' or 'primusrun' commands,
user accounts must be part of the "bumblebee" group.

You can add yourself (or any user) to the "bumblebee" group with:
  # gpasswd -a <username> bumblebee

EOF

install -D -m644 conf/bumblebee.conf %{buildroot}%{_sysconfdir}/bumblebee/bumblebee.conf

# Create nvidia-settings launcher script
cat << EOF > nvidia-settings-bumblebee
#!/bin/sh
optirun -b none %{_libdir}/nvidia-current/bin/nvidia-settings -c :8
EOF

install -D -m755 nvidia-settings-bumblebee %{buildroot}%{_bindir}/nvidia-settings-bumblebee
