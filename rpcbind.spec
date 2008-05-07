#
Summary:	Universal addresses to RPC program number mapper
Summary(pl.UTF-8):	Demon odwzorowujący adresy uniwersalne na numery programów RPC
Name:		rpcbind
Version:	0.1.5
Release:	0.1
License:	GPL
Group:		Daemons
Source0:	http://dl.sourceforge.net/sourceforge/rpcbind/%{name}-%{version}.tar.bz2
# Source0-md5:	adcf17feb72d942f38f91a9a90205a74
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch2:		%{name}-debug.patch
Patch3:		%{name}-warmstart.patch
Patch4:		%{name}-rpcuser.patch
Patch5:		%{name}-libwrap.patch
Patch6:		%{name}-syslog.patch
Patch7:		%{name}-iff_up.patch
# http://nfsv4.bullopensource.org/doc/tirpc_rpcbind.php
URL:		http://sourceforge.net/projects/rpcbind/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtirpc-devel
BuildRequires:	libwrap-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.1.6
Provides:	portmap
Provides:	user(rpc)
Obsoletes:	portmap
Conflicts:	clusternfs < 3.0-0.rc2.3
Conflicts:	flixengine < 8.0.8.2-1
Conflicts:	nfs-utils < 1.1.0-0.rc2.1
Conflicts:	quota-rquotad < 1:3.14-4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The rpcbind utility is a server that converts RPC program numbers into
universal addresses. It must be running on the host to be able to make
RPC calls on a server on that machine.

%description -l pl.UTF-8
Narzędzie rpcbind to serwer konwertujący numery programów RPC na
adresy uniwersalne. Musi działać na maszynie, aby można było wykonywać
wywołania RPC na serwerze na tej maszynie.

%prep
%setup -q
#%patch2 -p1
#%patch3 -p1
#%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}
%configure \
	--enable-libwrap \
	--enable-warmstarts \
	--with-statedir=/var/lib/rpcbind \
	--with-rpcuser=rpc
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
