%define sname	speechd
%define major	2
%define libname	%mklibname %{sname} %{major}
%define devname	%mklibname %{sname} -d

%bcond_without alsa
%bcond_without pulse
%bcond_without nas
%bcond_without espeak
%bcond_without libao

Summary:	Speech Dispatcher provides a device independent layer for speech synthesis
Name:		speech-dispatcher
Version:	0.8.1
Release:	1
Group:		System/Libraries
License:	GPLv2
Url:		http://www.freebsoft.org/speechd
Source0:	http://www.freebsoft.org/pub/projects/speechd/%{name}-%{version}.tar.gz
# Fedora systemd unit
Source1:	speech-dispatcherd.service
Source2:	speech-dispatcher.logrotate
Source3:	speech-dispatcherd.default
Source4:	speech-dispatcher-user-pulse.example
Source10:	%{name}.rpmlintrc

BuildRequires:	texinfo
BuildRequires:	pkgconfig(dotconf)
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
BuildRequires:	espeak-devel
%endif
%if %{with libao}
BuildRequires:	pkgconfig(ao)
%endif

%description
This is the Speech Dispatcher project (speech-dispatcher). It is a part of the
Free(b)soft project, which is intended to allow blind and visually impaired
people to work with computer and Internet based on free software.

%post
%_post_service speech-dispatcherd || :

%preun
%_preun_service speech-dispatcherd || :

%files -f %{name}.lang
%doc AUTHORS NEWS README COPYING INSTALL
%doc ChangeLog speech-dispatcher-user-pulse.example
%{_bindir}/spd-say
%{_bindir}/spdsend
%{_bindir}/%{name}
%{_unitdir}/speech-dispatcherd.service
%config %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/speechd.conf
%config(noreplace) %{_sysconfdir}/%{name}/clients/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/modules/*.conf
%config(noreplace) %{_sysconfdir}/default/speech-dispatcherd
%{_libdir}/%{name}-modules
%{_libdir}/%{name}
%{_datadir}/sounds/%{name}
%{_infodir}/*
%{_logdir}/%{name}

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n %{libname}
This package provides the shared libraries for Speech Dispatcher.

%files -n %{libname}
%{_libdir}/libspeechd.so.%{major}*

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{name} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

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
%rename	python3-%{sname}

%description -n python-%{sname}
This package provides a Python library for communication 
with Speech Dispatcher.

%files -n python-%{sname}
%doc ChangeLog
%{_bindir}/spd-conf
%{py3_puresitedir}/speechd*

%prep
%setup -q
%apply_patches
cp -p %SOURCE4 .

%build
%ifarch x86_64
export am_cv_python_pyexecdir=%{py3_puresitedir}
%endif
%configure \
	--disable-static \
%if %{with alsa}
	--with-alsa \
%else
	--without-alsa \
%endif
%if %{with pulse}
	--with-pulse \
%else
	--without-pulse \
%endif
%if %{with nas}
	--with-nas \
%else
	--without-nas \
%endif
%if %{with espeak}
	--with-espeak \
%else
	--without-espeak \
%endif
%if %{with libao}
	--with-libao
%else
	--without-libao
%endif

%make

%install
%makeinstall_std

# remove duplicates with /etc conf files 
rm -rf %{buildroot}%{_datadir}/%{name}

# fix perm in _test.py
chmod +x %{buildroot}%{py3_puresitedir}/speechd/_test.py

# speech-dispatcher service
install -Dm 0644 %SOURCE1 %{buildroot}%{_unitdir}/speech-dispatcherd.service

# logrotate install
install -Dm 0644 %SOURCE2 %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# install the /etc/default configuration file
install -Dm 0644 %SOURCE3 %{buildroot}%{_sysconfdir}/default/speech-dispatcherd

# create the needed directory for logs
install -d -m 0755 %{buildroot}%{_logdir}/%{name}

# remove flite module from the default configuration in speechd.conf
sed -i -e "210 s:AddModule:#AddModule:g" %{buildroot}%{_sysconfdir}/%{name}/speechd.conf

%find_lang %{name}
