%define name    bumblebee
%define version 3.0
%define release 5

Name:           %{name}
Summary:        Bumblebee - support for NVidia Optimus laptops on Linux!
Version:        %{version}
Release:        %{release}
Source0:        http://bumblebee-project.org/%{name}-%{version}.tar.gz
Source1:	bumblebee-mdv.tar.gz
URL:            http://bumblebee-project.org

Group:          System/Kernel and hardware
License:        GPLv3
Requires:       x11-driver-video-nvidia-current VirtualGL dkms-bbswitch gettext
BuildRequires:  help2man X11-devel glib2-devel gettext
BuildRequires:	%{_lib}bsd-devel >= 0.2.0

%description
Bumblebee daemon is a rewrite of the original Bumblebee service, providing an elegant and stable means of managing Optimus hybrid graphics chipsets.
A primary goal of this project is to not only enable use of the discrete GPU for rendering, but also to enable smart power management of the dGPU when it's not in use.

%prep
%setup -q -a1

%build
%configure CONF_DRIVER=nvidia CONF_DRIVER_MODULE_NVIDIA=nvidia-current CONF_LDPATH_NVIDIA=/usr/lib64/nvidia-current:/usr/lib/nvidia-current CONF_MODPATH_NVIDIA=/usr/lib64/nvidia-current/xorg,/usr/lib/nvidia-current/xorg,/usr/lib64/xorg/extra-modules,/usr/lib64/xorg/modules,/usr/lib/xorg/extra-modules,/usr/lib/xorg/modules
%make

%install
%makeinstall
rm -f %{buildroot}/%{_datadir}/doc/bumblebee/README.markdown %{buildroot}/%{_datadir}/doc/bumblebee/RELEASE_NOTES_3_0
mkdir -p %{buildroot}/etc/systemd/system
cp scripts/systemd/bumblebeed.service %{buildroot}/etc/systemd/system/bumblebeed.service

mv %{buildroot}/%{_bindir}/optirun %{buildroot}/%{_bindir}/optirun-bin
install -m 0755 bumblebee-mdv/bin/bumblebee-add-groups %buildroot/%{_bindir}/bumblebee-add-groups
install -m 0755 bumblebee-mdv/bin/optirun %buildroot/%{_bindir}/optirun

mkdir -p %{buildroot}/%{_datadir}/polkit-1/actions
cp -a bumblebee-mdv/bin/bumblebee.add-groups.policy %{buildroot}/%{_datadir}/polkit-1/actions

# translations
find bumblebee-mdv/po/* -type d | \
while read d
do
    lang=`basename $d`
    mkdir -p %buildroot/%_datadir/locale/$lang/LC_MESSAGES
    msgfmt -o %buildroot/%_datadir/locale/$lang/LC_MESSAGES/bumblebee-add-groups.mo $d/bumblebee-add-groups.po
done

#icons
mkdir -p %{buildroot}/%{_iconsdir}
cp bumblebee-mdv/bumblebee.png %{buildroot}/%{_iconsdir}

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
%{_bindir}/optirun-bin
%{_bindir}/bumblebee-add-groups
%{_bindir}/bumblebee-bugreport
%{_mandir}/man1/bumblebeed.1*
%{_mandir}/man1/optirun.1*
%{_iconsdir}/bumblebee.png
%{_localedir}/*
%{_datadir}/polkit-1/actions/bumblebee.add-groups.policy

%pre
# Add bumblebee group

	if getent group bumblebee > /dev/null
	then
	: # group already exists
	else
	groupadd -r bumblebee 2>/dev/null || :
	fi

%post
update-alternatives --set gl_conf /etc/ld.so.conf.d/GL/standard.conf
systemctl enable bumblebeed.service
systemctl start bumblebeed.service

%postun
groupdel bumblebee
