%define name    bumblebee
%define version 3.0
%define release 1

Name:           %{name}
Summary:        Bumblebee - support for NVidia Optimus laptops on Linux!
Version:        %{version}
Release:        %{release}
Source0:        http://bumblebee-project.org/%{name}-%{version}.tar.gz
URL:            http://bumblebee-project.org

Group:          System/Kernel and hardware
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
License:        GPLv3
Requires:       x11-driver-video-nvidia-current VirtualGL dkms-bbswitch
BuildRequires:  help2man X11-devel glib2-devel
BuildRequires:	%{_lib}bsd-devel >= 0.2.0

%description
Bumblebee daemon is a rewrite of the original Bumblebee service, providing an elegant and stable means of managing Optimus hybrid graphics chipsets.
A primary goal of this project is to not only enable use of the discrete GPU for rendering, but also to enable smart power management of the dGPU when it's not in use.

%prep
%setup -q

%build
%configure CONF_DRIVER=nvidia CONF_DRIVER_MODULE_NVIDIA=nvidia-current CONF_LDPATH_NVIDIA=/usr/lib64/nvidia-current:/usr/lib/nvidia-current CONF_MODPATH_NVIDIA=/usr/lib64/nvidia-current/xorg,/usr/lib/nvidia-current/xorg,/usr/lib64/xorg/extra-modules,/usr/lib64/xorg/modules,/usr/lib/xorg/extra-modules,/usr/lib/xorg/modules
%make

%install
rm -rf %{buildroot}
%makeinstall
rm -f %{buildroot}/usr/share/doc/bumblebee/README.markdown %{buildroot}/usr/share/doc/bumblebee/RELEASE_NOTES_3_0
mkdir -p %{buildroot}/etc/systemd/system
cp scripts/systemd/bumblebeed.service %{buildroot}/etc/systemd/system/bumblebeed.service

%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root)
%doc README.markdown doc/RELEASE_NOTES_3_0
%{_sysconfdir}/bash_completion.d/bumblebee
%{_sysconfdir}/bumblebee/bumblebee.conf
%{_sysconfdir}/bumblebee/xorg.conf.nouveau
%{_sysconfdir}/bumblebee/xorg.conf.nvidia
%{_sysconfdir}/systemd/system/bumblebeed.service
%{_sbindir}/bumblebeed
%{_bindir}/optirun
%{_bindir}/bumblebee-bugreport
%{_mandir}/man1/bumblebeed.1*
%{_mandir}/man1/optirun.1*

%post
if
    getent group bumblebee >/dev/null
then
    : OK group bumblebee already present
else
    groupadd -r bumblebee 2>/dev/null || :
fi
update-alternatives --set gl_conf /etc/ld.so.conf.d/GL/standard.conf
systemctl enable bumblebeed.service
systemctl start bumblebeed.service

%changelog 
