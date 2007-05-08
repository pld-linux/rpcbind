Summary:	Universal addresses to RPC program number mapper
Name:		rpcbind
Version:	0.1.4
Release:	0.4
License:	GPL
Group:		Daemons
Source0:	http://nfsv4.bullopensource.org/tarballs/rpcbind/%{name}-%{version}.tar.bz2
# Source0-md5:	280539aa1f8975b1318690cd903f858a
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-build.patch
Patch1:		%{name}-format.patch
Patch2:		%{name}-warmstart.patch
Patch3:		%{name}-rpcuser.patch
URL:		http://nfsv4.bullopensource.org/doc/tirpc_rpcbind.php
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtirpc-devel
BuildRequires:	libwrap-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	/sbin/chkconfig
Requires:	rc-scripts
Provides:	portmap
Provides:	user(rpc)
Obsoletes:	portmap
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The rpcbind utility is a server that converts RPC program numbers into
universal addresses.  It must be running on the host to be able to make
RPC calls on a server on that machine.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
cp -f /usr/share/automake/config.sub .
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/sbin,%{_sbindir},/etc/{sysconfig,rc.d/init.d}} \
	$RPM_BUILD_ROOT{%{_mandir}/man8,%{_var}/lib/%{name}}

install src/rpcbind $RPM_BUILD_ROOT/sbin
install src/rpcinfo $RPM_BUILD_ROOT%{_sbindir}

install man/{rpcbind,rpcinfo}.8 $RPM_BUILD_ROOT%{_mandir}/man8

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/rpcbind
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/rpcbind

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%useradd -u 22 -d /usr/share/empty -s /bin/false -c "Portmapper RPC User" -g nobody rpc

%post
/sbin/chkconfig --add rpcbind
%service rpcbind restart

%postun
if [ "$1" = "0" ]; then
	%userremove rpc
fi

%preun
if [ "$1" = "0" ]; then
	%service -q rpcbind stop
	/sbin/chkconfig --del rpcbind
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README
%attr(754,root,root) /etc/rc.d/init.d/rpcbind
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/rpcbind
%attr(755,root,root) /sbin/*
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man8/*.8*
%dir %attr(700,rpc,root) %{_var}/lib/%{name}
