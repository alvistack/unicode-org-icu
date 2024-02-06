# Copyright 2024 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%define debug_package %{nil}

%global source_date_epoch_from_changelog 0

Name: icu74
Epoch: 100
Version: 74.2
Release: 1%{?dist}
Summary: International Components for Unicode
License: ICU
URL: https://github.com/unicode-org/icu/tags
Source0: %{name}_%{version}.orig.tar.gz
%if 0%{?rhel} == 7
BuildRequires: devtoolset-11
BuildRequires: devtoolset-11-gcc
BuildRequires: devtoolset-11-gcc-c++
BuildRequires: devtoolset-11-libatomic-devel
%endif
BuildRequires: autoconf
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: python3
BuildRequires: prename
Requires: libicu74 = %{epoch}:%{version}-%{release}

%description
Tools and utilities for developing with icu.

%package -n libicu74
Summary: International Components for Unicode - libraries

%description -n libicu74
The International Components for Unicode (ICU) libraries provide
robust and full-featured Unicode services on a wide variety of
platforms. ICU supports the most current version of the Unicode
standard, and they provide support for supplementary Unicode
characters (needed for GB 18030 repertoire support).
As computing environments become more heterogeneous, software
portability becomes more important. ICU lets you produce the same
results across all the various platforms you support, without
sacrificing performance. It offers great flexibility to extend and
customize the supplied services.

%package  -n libicu-devel
Summary: Development files for International Components for Unicode
Requires: libicu74 = %{epoch}:%{version}-%{release}
Requires: pkgconfig

%description -n libicu-devel
Includes and definitions for developing with icu.

%{!?endian: %global endian %(%{__python3} -c "import sys;print (0 if sys.byteorder=='big' else 1)")}
# " this line just fixes syntax highlighting for vim that is confused by the above and continues literal

%prep
%setup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .
%autopatch -p1

%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-11/enable
%endif
pushd icu4c/source
autoconf
CFLAGS='%optflags -fno-strict-aliasing'
CXXFLAGS='%optflags -fno-strict-aliasing'
# Endian: BE=0 LE=1
%if ! 0%{?endian}
CPPFLAGS='-DU_IS_BIG_ENDIAN=1'
%endif

#rhbz856594 do not use --disable-renaming or cope with the mess
OPTIONS='--with-data-packaging=library --disable-samples'
%if 0%{?debugtrace}
OPTIONS=$OPTIONS' --enable-debug --enable-tracing'
%endif
%configure $OPTIONS

#rhbz#225896
sed -i 's|-nodefaultlibs -nostdlib||' config/mh-linux
#rhbz#813484
sed -i 's| \$(docfilesdir)/installdox||' Makefile
# There is no source/doc/html/search/ directory
sed -i '/^\s\+\$(INSTALL_DATA) \$(docsrchfiles) \$(DESTDIR)\$(docdir)\/\$(docsubsrchdir)\s*$/d' Makefile
# rhbz#856594 The configure --disable-renaming and possibly other options
# result in icu/source/uconfig.h.prepend being created, include that content in
# icu/source/common/unicode/uconfig.h to propagate to consumer packages.
test -f uconfig.h.prepend && sed -e '/^#define __UCONFIG_H__/ r uconfig.h.prepend' -i common/unicode/uconfig.h

# more verbosity for build.log
sed -i -r 's|(PKGDATA_OPTS = )|\1-v |' data/Makefile

%make_build

%install
%make_install %{?_smp_mflags} -C icu4c/source
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so.*
rm -rf $RPM_BUILD_ROOT%{_bindir}
rm -rf $RPM_BUILD_ROOT%{_sbindir}
rm -rf $RPM_BUILD_ROOT%{_mandir}

%check

%files
%license icu4c/LICENSE

%files -n libicu74
%{_libdir}/*.so.*

%files -n libicu-devel
%dir %{_datadir}/icu
%dir %{_datadir}/icu/*
%{_datadir}/icu/*/*
%{_includedir}/unicode
%{_libdir}/*.so
%{_libdir}/icu
%{_libdir}/pkgconfig/*.pc

%changelog
