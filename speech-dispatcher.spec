# Allow plugins to reference symbols defined in the server
%define _disable_ld_no_undefined 1

%define sname speechd
%define major 2
%define libname %mklibname %{sname} %{major}
%define devname %mklibname %{sname} -d

%bcond_without alsa
%bcond_without pulse
%bcond_with nas
%bcond_without espeak
%bcond_without libao
%bcond_with voxin

Summary:	Speech Dispatcher provides a device independent layer for speech synthesis
Name:		speech-dispatcher
Version:	0.12.1
Release:	1
Group:		System/Libraries
License:	GPLv2
Url:		https://www.freebsoft.org/speechd
Source0:	https://github.com/brailcom/speechd/releases/download/%{version}/%{name}-%{version}.tar.gz
Source1:	http://www.freebsoft.org/pub/projects/sound-icons/sound-icons-0.1.tar.gz
Source2:	speech-dispatcher.logrotate
Source3:	speech-dispatcherd.default
Source4:	speech-dispatcher-user-pulse.example
##Patch0:		0001-Remove-pyxdg-dependency.patch

BuildRequires:	texinfo
BuildRequires:	intltool
BuildRequires:	libtool-devel
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(dotconf)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	pkgconfig(python3)
%if %{with alsa}
BuildRequires:	pkgconfig(alsa)
%endif
%if %{with pulse}
BuildRequires:	pkgconfig(libpulse)
%endif
%if %{with nas}
BuildRequires:	nas-devel
%endif
%if %{with espeak}
BuildRequires:	pkgconfig(espeak-ng)
%endif
%if %{with libao}
BuildRequires:	pkgconfig(ao)
%endif
BuildRequires:	pkgconfig(sndfile)

%description
This is the Speech Dispatcher project (speech-dispatcher). It is a part of the
Free(b)soft project, which is intended to allow blind and visually impaired
people to work with computer and Internet based on free software.

%files -f %{name}.lang
%doc AUTHORS NEWS INSTALL
%{_unitdir}/%{name}d.service
%{_bindir}/spd-say
%{_bindir}/spdsend
%{_bindir}/%{name}
%config %{_sysconfdir}/logrotate.d/%{name}
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/conf
%dir %{_sysconfdir}/%{name}/clients
%dir %{_sysconfdir}/%{name}/modules
%config(noreplace) %{_sysconfdir}/%{name}/speechd.conf
%config(noreplace) %{_sysconfdir}/%{name}/conf/speechd.conf
%config(noreplace) %{_sysconfdir}/%{name}/clients/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/modules/*.conf
%config(noreplace) %{_sysconfdir}/default/speech-dispatcherd
#{_libdir}/%{name}-modules
%{_libexecdir}/%{name}-modules
%{_libdir}/%{name}
%{_datadir}/sounds/%{name}
%{_infodir}/*
%{_logdir}/%{name}
%{_prefix}/lib/systemd/user/speech-dispatcher.service
%{_prefix}/lib/systemd/user/speech-dispatcher.socket
%{_mandir}/man1/spd-conf.1*
%{_mandir}/man1/spd-say.1*
%{_mandir}/man1/speech-dispatcher.1*

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n %{libname}
This package provides the shared libraries for Speech Dispatcher.

%files -n %{libname}
%{_libdir}/libspeechd.so.%{major}*
%{_libdir}/libspeechd_module.so.0*

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
This package contains development files for %{name}.

%files -n %{devname}
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/%{name}.pc

%package -n python-%{sname}
Summary:	A Python library for communication with Speech Dispatcher
Group:		System/Libraries
Requires:	%{name} = %{version}-%{release}
%rename		python3-%{sname}

%description -n python-%{sname}
This package provides a Python library for communication
with Speech Dispatcher.

%files -n python-%{sname}
%{_bindir}/spd-conf
%{python_sitearch}/speechd*

%prep
%autosetup -p1 -a1
#tar xf %{SOURCE1}

%build
%configure \
	--disable-static \
	--without-oss \
	--with-kali=no \
	--with-baratinoo=no \
	--with-ibmtts=no \
	--without-flite \
 	--with-systemdsystemunitdir=%{_unitdir} \
	--with-systemduserunitdir=%{_prefix}/lib/systemd/user/ \
 	--without-espeak \
%if %{with alsa}
	--with-alsa \
%else
	--without-alsa \
%endif
%if %{with pulse}
	--with-pulse \
	--with-default-audio-method=pulse \
%else
	--without-pulse \
%endif
%if %{with nas}
	--with-nas \
%else
	--without-nas \
%endif
%if %{with espeak}
	--with-espeak-ng \
%else
	--without-espeak-ng \
%endif
%if %{with libao}
	--with-libao \
%else
	--without-libao \
%endif
%if %{with voxin}
	--with-voxin \
%else
	--without-voxin \
%endif
	%nil
%make_build

%install
%make_install

#Remove %{_infodir}/dir file
rm -f %{buildroot}%{_infodir}/dir

find %{buildroot} -name '*.la' -delete

# Move the config files from /usr/share to /etc
mkdir -p %{buildroot}%{_sysconfdir}/speech-dispatcher/clients
mkdir -p %{buildroot}%{_sysconfdir}/speech-dispatcher/modules
mv %{buildroot}%{_datadir}/speech-dispatcher/conf/clients/* %{buildroot}%{_sysconfdir}/speech-dispatcher/clients
mv %{buildroot}%{_datadir}/speech-dispatcher/conf/modules/* %{buildroot}%{_sysconfdir}/speech-dispatcher/modules

# (tpg) use our config
mkdir -p %{buildroot}%{_sysconfdir}/speech-dispatcher/conf
cp %{SOURCE4} %{buildroot}%{_sysconfdir}/speech-dispatcher/conf/speechd.conf

# remove duplicates with /etc conf files
rm -rf %{buildroot}%{_datadir}/%{name}

chmod +x %{buildroot}%{python_sitearch}/speechd/_test.py

# logrotate install
install -Dm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# install the /etc/default configuration file
install -Dm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/default/speech-dispatcherd

# create the needed directory for logs
install -d -m 0755 %{buildroot}%{_logdir}/%{name}

# remove flite module from the default configuration in speechd.conf
sed -i -e "210 s:AddModule:#AddModule:g" %{buildroot}%{_sysconfdir}/%{name}/speechd.conf

# enable pulseaudio as default with a fallback to alsa
sed -i -e 's/# AudioOutputMethod "pulse,alsa"/AudioOutputMethod "pulse,alsa"/' %{buildroot}%{_sysconfdir}/speech-dispatcher/speechd.conf

%find_lang %{name}
