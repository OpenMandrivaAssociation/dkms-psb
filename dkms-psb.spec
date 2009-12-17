%define module psb
%define name dkms-%{module}
%define version 4.41.1
%define date 0
%define release %mkrel 6
%if %{date}
%define dkms_ver %{date}-%{release}
%define sname %{module}-kmd-%{date}
%define dname %{sname}
%else
%define dkms_ver %{version}-%{release}
%define sname %{module}-kernel-source_%{version}.orig
%define dname %{module}-kernel-source-%{version}
%endif

Summary: Poulsbo DRM driver
Name: %{name}
Version: %{version}
Release: %{release}
# http://moblin.org/repos/projects/psb-kmd.git
# DATE=20081006; git archive --format=tar --prefix=psb-kmd-$DATE/ origin/GASTON | gzip > psb-kmd-$DATE.tar.gz
Source0: http://ppa.launchpad.net/ubuntu-mobile/ppa/ubuntu/pool/main/p/psb-kernel-source/%{sname}.tar.gz
# (blino) fix build with 2.6.29
Patch0: psb-kmd-4.34-current_euid.patch
Patch1: psb-kernel-source-4.41.1-i2c-intelfb.patch
Patch2: psb-kmod-4.41.1_irqreturn.patch
Patch3: psb-kernel-source-4.41.1-agp_memory.patch
Patch4: psb-kernel-source-4.41.1-dev_set_name.patch
# rename drm.ko as drm-psb.ko (and make psb.ko depend on drm-psb)
Patch5:	psb-kernel-source-4.41.1-drmpsb.patch
# make udev create device node
Patch6: psb-kernel-source-4.41.1-devt.patch
# #51562
Patch7:	psb-kernel-source-4.41.1-edid-crash.patch
# fix build on 2.6.32, from gentoo (#56224)
Patch8:	psb-kernel-source-4.41.1-2.6.32.patch
License: GPL
Group: System/Kernel and hardware
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Url: http://git.moblin.org/cgit.cgi/deprecated/psb-kmd/
BuildArch: noarch
Requires(post): dkms
Requires(preun): dkms
Obsoletes: psb-preload <= 4.41.1-1mdv2010.0

%description
This is a DRM driver for the video chipset from the Poulsbo SCH.

%prep
%setup -q -n %{dname}
%patch0 -p1 -b .current_euid
%patch1 -p1 -b .i2c-intelfb
%patch2 -p1 -b .irqreturn
%patch3 -p1 -b .agp_memory
%patch4 -p1 -b .dev_set_name
%patch5 -p1 -b .drmpsb
%patch6 -p1 -b .devt
%patch7 -p1 -b .edid

cat > dkms.conf <<EOF
PACKAGE_NAME=%{module}
PACKAGE_VERSION=%{dkms_ver}
MAKE[0]="make LINUXDIR=\${kernel_source_dir} DRM_MODULES=psb"
BUILT_MODULE_NAME[0]=psb
BUILT_MODULE_NAME[1]=drm-psb
DEST_MODULE_LOCATION[0]=/kernel/drivers/gpu/drm
DEST_MODULE_LOCATION[1]=/kernel/drivers/gpu/drm
AUTOINSTALL=yes
EOF

# rename exported symbols with psb_ prefix
# so that they don't conflict with original drm module
prefix=psb_
exclude_files=drm_compat
files=$(find -name "*.[ch]" | grep -v $exclude_files)
rules=
for symbol in $(grep EXPORT_SYMBOL $files | perl -lne '/^.*EXPORT_SYMBOL(?:|_GPL)\((.*)\);/ and print $1'); do
  rules="s/\b$symbol\b/$prefix$symbol/g;$rules"
done
perl -pi -e $rules $files

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/src/%{module}-%{dkms_ver}/
tar c . | tar x -C %{buildroot}/usr/src/%{module}-%{dkms_ver}/

%clean
rm -rf %{buildroot}

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{module} -v %{dkms_ver}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{module} -v %{dkms_ver}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{module} -v %{dkms_ver}
:

%preun
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{module} -v %{dkms_ver} --all
:

%files
%defattr(-,root,root)
/usr/src/%{module}-%{dkms_ver}
