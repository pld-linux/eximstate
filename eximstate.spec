Summary:	Monitoring exim installations
Summary(pl):	Monitorowanie instalacji exima
Name:		eximstate
Version:	1.0
Release:	2
License:	GPL
Group:		Applications/Mail
Source0:	http://www.olliecook.net/projects/%{name}/%{name}.tar.gz
# Source0-md5:	e59355c849577dc5354e2614a5246aba
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}d.init
Source4:	%{name}d.sysconfig
Patch0:		%{name}-debug.patch
URL:		http://www.olliecook.net/projects/eximstate/
BuildRequires:	ncurses-devel
BuildRequires:	rrdtool-devel
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/eximstate
%define		_localstatedir	%{_var}/spool/%{name}

%description
eximstate is a server/client project for monitoring a number of Exim
installations. The clients are installed on each of the mailservers
running exim and the server runs on the monitoring server. Each client
reads the queue on the mail server and sends the total number of
messages, the number of frozen message, and the number of bounce
messages to the server. The server stores this data and uses RRDtool
to make a graphical representations of the data.

%description -l pl
eximstate to klient/serwer do monitorowania instalacji Exima. Klienci
instalowania na ka¿dym serwerze poczty pracuj±cym pod kontrol± Exima
oraz serwer pracuj±cy na serwerze monitoruj±cym. Ka¿dy klient czyta
kolejkê na serwerze pocztowym oraz przesy³a informacje o ca³kowitej
liczbie wiadomo¶ci, liczbie zamro¿onych wiadomo¶ci oraz licznie
wiadomo¶ci odbitych do serwera. Serwer eximstate zapisuje te dane oraz
u¿ywa RRDtoola w celu stworzenia graficznej reprezentacji danych.

%package client
Summary:	eximstate client
Summary(pl):	Klient eximstate
Group:		Networking
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	exim >= 3.0.0

%description client
eximstate is a server/client project for monitoring a number of Exim
installations. This is client.

%description client -l pl
eximstate to klient/serwer do monitorowania instalacji Exima. To jest
klient.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	CPPFLAGS="-I%{_includedir}/ncurses" \
	--with-rrdtool=%{_prefix}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_localstatedir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp $RPM_BUILD_ROOT%{_sbindir}/graphrrd.sh .
sed -e 's#%{_prefix}/local/apache/htdocs/#/srv/httpd/html/%{name}/#g' graphrrd.sh \
	> $RPM_BUILD_ROOT%{_sbindir}/graphrrd.sh

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}d
install %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}d

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}d
if [ -f %{_var}/lock/subsys/%{name}d ]; then
	/etc/rc.d/init.d/%{name}d restart 1>&2
else
	echo "Run \"/usr/sbin/makenewrrd.sh <host>\" for each your monitored host."
	echo "Run \"/etc/rc.d/init.d/%{name}d start\" to start %{name}d daemon."
fi

%preun
if [ "$1" = "0" -a -f %{_var}/lock/subsys/%{name}d ]; then
	/etc/rc.d/init.d/%{name}d stop 1>&2
fi
/sbin/chkconfig --del %{name}d

%post client
/sbin/chkconfig --add %{name}
if [ -f %{_var}/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi

%preun client
if [ "$1" = "0" -a -f %{_var}/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} stop 1>&2
fi
/sbin/chkconfig --del %{name}

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README
%attr(755,root,root) %{_bindir}/exitop
%attr(755,root,root) %{_sbindir}/eximstated
%attr(755,root,root) %{_sbindir}/*.sh

%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}d.conf
%attr(755,root,root) %{_var}/spool/%{name}

%attr(754,root,root) /etc/rc.d/init.d/%{name}d
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}d

%files client
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/eximstate
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}.conf

%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
