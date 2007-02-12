# TODO: what non-existing directory in /home/services/httpd/html is used for???
Summary:	Monitoring exim installations
Summary(pl.UTF-8):	Monitorowanie instalacji exima
Name:		eximstate
Version:	1.1
Release:	3
License:	GPL
Group:		Applications/Mail
Source0:	http://www.olliecook.net/projects/eximstate/releases/%{name}-%{version}.tar.gz
# Source0-md5:	e59355c849577dc5354e2614a5246aba
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}d.init
Source4:	%{name}d.sysconfig
Patch0:		%{name}-debug.patch
URL:		http://www.olliecook.net/projects/eximstate/
BuildRequires:	ncurses-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.2.10
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

%description -l pl.UTF-8
eximstate to klient/serwer do monitorowania instalacji Exima. Klienty
zainstalowane są na każdym serwerze poczty pracującym pod kontrolą
Exima natomiast serwer eximstate na serwerze monitorującym. Każdy
klient czyta kolejkę na serwerze pocztowym oraz przesyła informacje o
całkowitej liczbie wiadomości, liczbie wiadomości zamrożonych oraz
odbitych. Serwer eximstate zapisuje te dane oraz używa RRDtoola w celu
stworzenia graficznej reprezentacji danych.

%package client
Summary:	eximstate client
Summary(pl.UTF-8):	Klient eximstate
Group:		Networking
Requires(post,preun):	/sbin/chkconfig
Requires:	exim >= 3.0.0
Requires:	rc-scripts

%description client
eximstate is a server/client project for monitoring a number of Exim
installations. This package contains client.

%description client -l pl.UTF-8
eximstate to klient/serwer do monitorowania instalacji Exima. Ten
pakiet zawiera klienta.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	CPPFLAGS="-I/usr/include/ncurses" \
	--with-rrdtool=%{_prefix}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_localstatedir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp $RPM_BUILD_ROOT%{_sbindir}/graphrrd.sh .
sed -e 's#%{_prefix}/local/apache/htdocs/#/home/services/httpd/html/%{name}/#g' graphrrd.sh \
	> $RPM_BUILD_ROOT%{_sbindir}/graphrrd.sh

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}d
install %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}d

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}d
if [ "$1" = 1 ]; then
	echo "Run \"%{_sbindir}/makenewrrd.sh <host>\" for each your monitored host."
fi
%service %{name}d restart "%{name}d daemon"

%preun
if [ "$1" = "0" ]; then
	%service %{name}d stop
	/sbin/chkconfig --del %{name}d
fi

%post client
/sbin/chkconfig --add %{name}
%service %{name} restart "%{name} daemon"

%preun client
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

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
