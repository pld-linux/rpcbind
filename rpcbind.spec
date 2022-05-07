#
# Conditional build:
%bcond_with	rmtcalls	# Remote Calls

Summary:	Universal addresses to RPC program number mapper
Summary(pl.UTF-8):	Demon odwzorowujący adresy uniwersalne na numery programów RPC
Name:		rpcbind
Version:	1.2.6
Release:	1
License:	BSD
Group:		Daemons
Source0:	https://downloads.sourceforge.net/rpcbind/%{name}-%{version}.tar.bz2
# Source0-md5:	2d84ebbb7d6fb1fc3566d2d4b37f214b
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-libwrap.patch
Patch1:		%{name}-syslog.patch
Patch2:		%{name}-sunrpc.patch
Patch3:		%{name}-nss.h.patch
Patch4:		%{name}-systemd.patch
Patch6:		%{name}-tcp-addrs.patch
# http://nfsv4.bullopensource.org/doc/tirpc_rpcbind.php
URL:		http://sourceforge.net/projects/rpcbind/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake
BuildRequires:	libtirpc-devel >= 1:1.0.1
BuildRequires:	libtool
BuildRequires:	libwrap-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.623
BuildRequires:	systemd-devel
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.1.6
Requires:	systemd-units >= 0.38
Provides:	portmap = 8.0
Provides:	user(rpc)
Obsoletes:	portmap < 6.1
Obsoletes:	rpcbind-systemd < 0.2.0-5
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
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch6 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--sbindir=/sbin \
	--bindir=%{_sbindir} \
	--enable-libwrap \
	%{?with_rmtcalls:--enable-rmtcalls} \
	--enable-warmstarts \
	--with-statedir=/var/lib/rpcbind \
	--with-rpcuser=rpc \
	--with-systemdsystemunitdir=%{systemdunitdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/sbin,%{_sbindir},/etc/{sysconfig,rc.d/init.d},/var/lib/rpcbind}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/rpcbind
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/rpcbind

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%useradd -u 22 -d /usr/share/empty -s /bin/false -c "Portmapper RPC User" -g nobody rpc

%post
/sbin/chkconfig --add rpcbind
%service rpcbind restart
%systemd_post rpcbind.service

%postun
if [ "$1" = "0" ]; then
	%userremove rpc
fi
%systemd_reload

%preun
if [ "$1" = "0" ]; then
	%service -q rpcbind stop
	/sbin/chkconfig --del rpcbind
fi
%systemd_preun rpcbind.service

%triggerpostun -- %{name} < 0.2.0-5
if [ -f /etc/sysconfig/rpcbind ]; then
	. /etc/sysconfig/rpcbind
	[ "$RPCBIND_VERBOSE" = "no" ] || RPCBIND_OPTIONS="-l"
	[ "$RPCBIND_INSECURE" = "yes" ] && RPCBIND_OPTIONS="$RPCBIND_OPTIONS -i"
	for a in $RPCBIND_ADDRESSES ; do
		RPCBIND_OPTIONS="$RPCBIND_OPTIONS -h $a"
	done
	[ -z "$RPCBIND_OPTIONS" ] && exit 0
	%{__cp} -f /etc/sysconfig/rpcbind /etc/sysconfig/rpcbind.rpmsave
	echo >>/etc/sysconfig/rpcbind
	echo "# Added by rpm trigger" >>/etc/sysconfig/rpcbind
	echo "RPCBIND_OPTIONS=\"$RPCBIND_OPTIONS\"" >> /etc/sysconfig/rpcbind
fi
%systemd_trigger rpcbind.service

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README
%attr(754,root,root) /etc/rc.d/init.d/rpcbind
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/rpcbind
%attr(755,root,root) /sbin/rpcbind
%attr(755,root,root) %{_sbindir}/rpcinfo
%{_mandir}/man8/rpcbind.8*
%{_mandir}/man8/rpcinfo.8*
%dir %attr(700,rpc,root) %{_var}/lib/%{name}
%{systemdunitdir}/rpcbind.service
%{systemdunitdir}/rpcbind.socket
