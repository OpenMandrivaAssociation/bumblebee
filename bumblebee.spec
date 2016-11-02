# Use nouveau driver by default
%bcond_with nvidia

Name:			bumblebee
Summary:		Bumblebee - support for NVidia Optimus laptops on Linux!
Version:		3.2.1
Release:		1
Source0:		http://bumblebee-project.org/%{name}-%{version}.tar.gz
Source1:		bumblebee-mdv.tar.gz
URL:			http://bumblebee-project.org

Group:			System/Kernel and hardware
License:		GPLv3
Requires:		VirtualGL
Requires:		dkms-bbswitch
Requires:		gettext
BuildRequires:	help2man gettext
BuildRequires:	pkgconfig(glib-2.0) pkgconfig(x11)
BuildRequires:	pkgconfig(libbsd) >= 0.2.0
Requires(post,postun): rpm-helper
%if %{with nvidia}
Suggests:		x11-driver-video-nvidia-current
%else
Requires:		x11-driver-video-nouveau
%endif

%description
Bumblebee daemon is a rewrite of the original Bumblebee service, providing an
elegant and stable means of managing Optimus hybrid graphics chipsets.

A primary goal of this project is to not only enable use of the discrete GPU
for rendering, but also to enable smart power management of the dGPU when
it's not in use.

%prep
%setup -q -a1

%build
%configure2_5x \

%if %{with nvidia}
		CONF_DRIVER=nvidia \
	 	CONF_DRIVER_MODULE_NVIDIA=nvidia-current \
	 	%else
	 	CONF_DRIVER=nouveau \
	 	%endif
	 	%ifarch x86_64
	 	CONF_LDPATH_NVIDIA=%{_usr}/lib/nvidia-current:%{_libdir}/nvidia-current \
	 	CONF_MODPATH_NVIDIA=%{_usr}/lib/nvidia-current/xorg,%{_libdir}/nvidia-current/xorg,%{_usr}/lib/xorg/modules,%{_libdir}/xorg/modules,%{_usr}/lib/xorg/extra-modules,%{_usr}/xorg/extra-modules
	 	%else
	 	CONF_LDPATH_NVIDIA=%{_usr}/lib/nvidia-current \
	 	CONF_MODPATH_NVIDIA=%{_usr}/lib/nvidia-current/xorg,%{_usr}/lib/xorg/modules,%{_usr}/lib/xorg/extra-modules
%endif


%make

%install
%makeinstall_std
rm -f %{buildroot}/%{_datadir}/doc/bumblebee/README.markdown
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
%doc README.markdown
%{_sysconfdir}/bash_completion.d/bumblebee
%dir %{_sysconfdir}/bumblebee
%{_sysconfdir}/bumblebee/bumblebee.conf
%{_sysconfdir}/bumblebee/xorg.conf.nouveau
%{_sysconfdir}/bumblebee/xorg.conf.nvidia
%dir %{_sysconfdir}/bumblebee/xorg.conf.d
%{_sysconfdir}/bumblebee/xorg.conf.d/10-dummy.conf
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
/lib/udev/rules.d/99-bumblebee-nvidia-dev.rules

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
update-alternatives --set gl_conf /etc/ld.so.conf.d/GL/standard.conf

%systemd_post bumblebeed.service

%postun
if [ "$1" -eq "0" ]; then
	/usr/sbin/groupdel bumblebee
fi

%systemd_postun bumblebeed.service
