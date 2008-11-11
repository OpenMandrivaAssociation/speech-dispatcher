%define major		2
%define shortname	speechd
%define libname		%mklibname %shortname %major
%define develname	%mklibname %shortname -d

%define build_alsa	1
%define build_pulse	1
%define build_nas	1
%define build_espeak	1

%{?_without_alsa: %{expand: %%global build_alsa 0}}
%{?_with_alsa: %{expand: %%global build_alsa 1}}

%{?_without_pulse: %{expand: %%global build_pulse 0}}
%{?_with_pulse: %{expand: %%global build_pulse 1}}

%{?_without_nas: %{expand: %%global build_nas 0}}
%{?_with_nas: %{expand: %%global build_nas 1}}

%{?_without_espeak: %{expand: %%global build_espeak 0}}
%{?_with_espeak: %{expand: %%global build_espeak 1}}

Name:			speech-dispatcher
Version:		0.6.7
Release:		%mkrel 1
Summary:		Speech Dispatcher provides a device independent layer for speech synthesis
Group:			System/Libraries
License:		GPLv2
URL:			http://www.freebsoft.org/speechd
Source0:		http://www.freebsoft.org/pub/projects/speechd/%name-%version.tar.gz
# modified Fedora init script 
Source1:		speech-dispatcherd.init.mdv
Source2:		speech-dispatcher.logrotate
Source3:		speech-dispatcherd.default
Source4:		speech-dispatcher-user-pulse.example
Patch0:			fix-speech-dispatcher-cs-info-uninstall
Requires:		%libname = %version-%release
%if %build_alsa
BuildRequires:		libalsa-devel
%endif
%if %build_pulse
BuildRequires:		pulseaudio-devel
%endif
%if %build_nas
BuildRequires:		libnas-devel
%endif
%if %build_espeak
BuildRequires:		libespeak-devel
%endif
BuildRequires:		libdotconf-devel
BuildRequires:		python-devel
BuildRequires:		texinfo
Buildroot:		%_tmppath/%name-%version-buildroot

%description
This is the Speech Dispatcher project (speech-dispatcher). It is a part of the
Free(b)soft project, which is intended to allow blind and visually impaired
people to work with computer and Internet based on free software.

%post
%_install_info %name.info || :
%_install_info spd-say.info || :
%_install_info ssip.info || :
%_install_info %name-cs.info || :
%_post_service speech-dispatcherd || :

%preun
%_remove_install_info %name.info || :
%_remove_install_info spd-say.info || :
%_remove_install_info ssip.info || :
%_remove_install_info %name-cs.info || :
%_preun_service speech-dispatcherd || :

%files
%defattr(-,root,root,-)
%doc AUTHORS NEWS README COPYING INSTALL TODO 
%doc ChangeLog speech-dispatcher-user-pulse.example
%_bindir/cli*
%_bindir/connection_recovery
%_bindir/spd-say
%_bindir/spd_long_message
%_bindir/spd_run_test
%_bindir/spdsend
%_bindir/%name
%_initrddir/speech-dispatcherd
%config %_sysconfdir/logrotate.d/%name
%config(noreplace) %_sysconfdir/%name/speechd.conf
%config(noreplace) %_sysconfdir/%name/clients/*.conf
%config(noreplace) %_sysconfdir/%name/modules/*.conf
%config(noreplace) %_sysconfdir/default/speech-dispatcherd
%_sysconfdir/%name
%_libdir/%name-modules
%_libdir/%name
%_datadir/sounds/%name
%_infodir/*
%_logdir/%name

#--------------------------------------------------------------------------

%package -n		%libname
Summary:		Shared libraries for %name
Group:			System/Libraries

%description -n		%libname
This package provides the shared libraries for Speech Dispatcher.

%files -n		%libname
%defattr(-,root,root,-)
%doc COPYING ChangeLog
%_libdir/libspeechd.so.%{major}*

#--------------------------------------------------------------------------

%package -n		%develname
Summary:		Development files for %name
Group:			Development/Other
Requires:		%name = %version-%release
Provides:		%name-devel = %version-%release
Provides:		lib%name-devel = %version-%release

%description -n 	%develname
This package contains development files for %name.

%files -n		%develname
%defattr(-,root,root)
%_includedir/*
%_libdir/lib*.so
%_libdir/lib*.la
%_libdir/speech-dispatcher/lib*.la
%_libdir/speech-dispatcher/lib*.so

#--------------------------------------------------------------------------

%package -n 		python-%shortname
Summary:		A Python library for communication with Speech Dispatcher
Group:			System/Libraries
Requires:		%name = %version-%release
Requires:		python

%description -n		python-%shortname
This package provides a Python library for communication 
with Speech Dispatcher.

%files -n		python-%shortname
%defattr(-,root,root,-)
%doc ChangeLog
%_bindir/spd-conf
%python_sitelib/speechd*
%_datadir/sounds/%name/test.wav

#--------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p0
cp -p %SOURCE4 .

%build
%configure \
	--disable-static \
%if %build_alsa
	--with-alsa \
%else
	--without-alsa \
%endif
%if %build_pulse
	--with-pulse \
%else
	--without-pulse \
%endif
%if %build_nas
	--with-nas \
%else
	--without-nas \
%endif
%if %build_espeak
	--with-espeak
%else
	--without-espeak
%endif

%make

%install
rm -rf %buildroot
%makeinstall

# remove duplicates with /etc conf files 
rm -rf %buildroot%_datadir/%name

# rename some executables
mv %buildroot%_bindir/long_message %buildroot%_bindir/spd_long_message
mv %buildroot%_bindir/run_test %buildroot%_bindir/spd_run_test

# speech-dispatcherd service
install -d -m 0755 %buildroot%_initrddir
install -m 0755 %SOURCE1 %buildroot%_initrddir/speech-dispatcherd

# fix perm in _test.py
chmod +x %buildroot%python_sitelib/speechd/_test.py

# logrotate install
install -d -m 0755 %buildroot%_sysconfdir/logrotate.d
install -m 0644 %SOURCE2 %buildroot%_sysconfdir/logrotate.d/%name

# create the needed directory for logs
install -d -m 0755 %buildroot%_logdir/%name

# install the /etc/default configuration file
install -d -m 0755 %buildroot%_sysconfdir/default
install -m 0644 %SOURCE3 %buildroot%_sysconfdir/default/speech-dispatcherd

# remove flite module from the default configuration in speechd.conf
sed -i -e "210 s:AddModule:#AddModule:g" %buildroot%_sysconfdir/%name/speechd.conf

%clean
rm -rf %buildroot
