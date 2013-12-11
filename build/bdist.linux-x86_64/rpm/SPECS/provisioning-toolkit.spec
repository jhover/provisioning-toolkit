%define name provisioning-toolkit
%define version 0.9.0
%define unmangled_version 0.9.0
%define release 0

Summary: Utilities for automating VM management.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: John Hover <jhover@bnl.gov>
Packager: John Hover <jhover@bnl.gov>
Provides: provisioning-toolkit
Requires: python pexpect  pyOpenSSL >= 0.7
Url: https://www.racf.bnl.gov/experiments/usatlas/griddev/
BuildRequires: python-devel

%description
Utilities for automating VM management.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
