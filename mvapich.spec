%define mpi_device ch_gen2
# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.                                              
%define opt_cc gcc      
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and define to use                                           
#define opt_cflags              
%define opt_cxx g++
#define opt_cxxflags
%define opt_f77 gfortran
#define opt_fflags      
%define opt_fc gfortran
#define opt_fcflags    

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

#define _cc_name_suffix -gcc

%define namearch %{name}-%{_arch}%{?_cc_name_suffix}
%define namepsmarch %{name}-psm-%{_arch}%{?_cc_name_suffix}
%define mpidir %{_libdir}/%{name}
%define mpipsmdir %{_libdir}/%{name}-psm

Summary: MPI implementation over Infiniband RDMA-enabled interconnect
Name: mvapich
Version: 1.2.0
Release: 0.3562.5%{?dist}
License: BSD
Group: Development/Libraries
Source0: mvapich-%{version}-3562.tar.gz
Source1: macros.mvapich
Source2: mvapich.module.in
Source3: macros.mvapich-psm
Patch0: mvapich-1.0.1-limit.patch
URL: http://mvapich.cse.ohio-state.edu/
Requires: %{name}-common = %{version}-%{release}
BuildRequires: libibverbs-devel >= 1.1.3, libibumad-devel, perl, autoconf
BuildRequires: java, python
%ifarch x86_64
BuildRequires: infinipath-psm-devel
%endif
ExclusiveArch: i386 x86_64 ia64 ppc64
Provides: mpi
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %(test "%{compiler}" = "gcc" && echo 1 || echo 0)
BuildRequires: gcc-c++ gcc-gfortran
%endif

%description
Mvapich is a high performance and scalable MPI-1 implementation over Infiniband
and RDMA-enabled interconnects.  This implementation is based on  MPICH
and MVICH. MVAPICH is pronounced as `em-vah-pich''. 

%package devel
Summary: Development files for the mvapich package
Group: Development/Libraries
Requires: libibverbs-devel >= 1.1.3, libibumad-devel
Requires: %{name} = %{version}-%{release}
Provides: mpi-devel

%description devel
Development headers and compilers to be used with the mvapich base runtime
package

%package common
Summary: Common files used by the mvapich runtime
Group: Development/Libraries
BuildArch: noarch

%description common
Various non-arch specific files used by mvapich runtime package

%package static
Summary: Static libraries for the mvapich package
Group: Development/Libraries
Requires: %{name}-devel = %{version}-%{release}

%description static
Contains the static libraries from the mvapich package.  Static library usage
is generally discouraged, but provided in this separate package for those
who must have it.

%ifarch x86_64
%package psm
Summary: MPI implementation over QLogic infinipath-psm interconnect
Group: Development/Libraries
Requires: infinipath-psm
ExclusiveArch: x86_64

%description psm
Mvapich is a high performance and scalable MPI-1 implementation over Infiniband
and RDMA-enabled interconnects.  This implementation is based on  MPICH
and MVICH. MVAPICH is pronounced as `em-vah-pich''. 

%package psm-devel
Summary: Development files for the mvapich package
Group: Development/Libraries
Requires: libibverbs-devel >= 1.1.3, libibumad-devel
Requires: %{name} = %{version}-%{release}
Provides: mpi-devel
ExclusiveArch: x86_64

%description psm-devel
Development headers and compilers to be used with the mvapich base runtime
package

%package psm-static
Summary: Static libraries for the mvapich-psm package
Group: Development/Libraries
Requires: %{name}-devel = %{version}-%{release}
ExclusiveArch: x86_64

%description psm-static
Contains the static libraries from the mvapich-psm package.  Static
library usage is generally discouraged, but provided in this separate
package for those who must have it.
%endif

%prep
%setup -q -n %{name}-%{version}-3562
%patch0 -p1 -b .limit
# We need to do two compiles: one for psm, and one for regular.
mkdir .psm .non-psm
%ifarch x86_64
cp -r * .psm
%endif
mv * .non-psm
ln .non-psm/{BUILDID,CHANGELOG,COPYRIGHT*,INSTALL,LICENSE.TXT,README*} .
mv .non-psm/{doc,examples,www,share,installtest} .
ln -s ../{doc,examples,www,share,installtest} .non-psm

cd .non-psm
OPTIMIZATION_FLAG="-O3 -fno-strict-aliasing"
CONFIG_ENABLE_F77="--disable-f77"
CONFIG_ENABLE_F90="--enable-f90"
EXTRA_CFLAG=
MPE_FLAGS="--with-mpe"
conffile=mvapich.conf
buildidfile=BUILDID
#############################################################################
# Compiler definition
# GNU compilers
%if %(test "%{compiler}" = "gcc" && echo 1 || echo 0)
    export CC=gcc
    export CXX=g++
    gcc_ver=`gcc --version | head -1 | awk '{print$3}' | awk -F. '{print $1}'`
    # For systems with mixed gcc-fortran install.
    if [ $gcc_ver -gt 3 ]; then
        # new gcc version
        export FC=gfortran
        export F77=gfortran
        export F90=gfortran
        export F77_GETARGDECL=
    else
        # old gcc version
        export FC=g77
        export F77=g77
        export F90=g77
    fi
    export CFLAGS="-Wall"
    export FFLAGS="-fPIC"
    export CXXFLAGS="-fPIC"
    export F90FLAGS="-fPIC"
    export CONFIG_FLAGS=
    export COMPILER_CONFIG="--with-romio"
%endif
# Intel compiler
%if %(test "%{compiler}" = "intel" && echo 1 || echo 0)
    export CC=icc
    export CXX=icc
    export FC=ifort
    export F90=$FC
    export CFLAGS="-D__INTEL_COMPILER"
    export FFLAGS="-fPIC"
    export CXXFLAGS="-fPIC"
    export CCFLAGS="-lstdc++"
    export F90FLAGS=$FFLAGS
    export CONFIG_FLAGS=""
    export COMPILER_CONFIG="--enable-f90modules --with-romio"
%endif
# Pathscale compiler
%if %(test "%{compiler}" = "pathscale" && echo 1 || echo 0)
    export CC=pathcc
    export CXX=pathCC
    export FC=pathf90
    export F90=pathf90
    export F77=pathf90
    export CFLAGS=""
    export FFLAGS="-fPIC"
    export CXXFLAGS="-fPIC"
    export CCFLAGS=""
    export F90FLAGS=$FFLAGS
    export CONFIG_FLAGS=""
    export COMPILER_CONFIG="--enable-f90modules --with-romio"
%endif
# PGI compiler
%if %(test "%{compiler}" = "pgi" && echo 1 || echo 0)
    export CC=pgcc
    export CXX=pgCC
    export FC=pgf77
    export F90=pgf90
    export CFLAGS="-Msignextend -DPGI"
    export FFLAGS="-fPIC"
    export CXXFLAGS="-fPIC"
    export F90FLAGS=$FFLAGS
    export CONFIG_FLAGS=""
    export OPTIMIZATION_FLAG=""
%endif
# Sun Studio compiler
%if %(test "%{compiler}" = "sun" && echo 1 || echo 0)
    export CC=suncc
    export CXX=sunCC
    export F77=sunf77
    export F90=sunf90
    export CFLAGS=""
    export FFLAGS="-fPIC"
    export CXXFLAGS="-fPIC"
    export F90FLAGS=$FFLAGS
    export CONFIG_FLAGS=""
    export OPTIMIZATION_FLAG="-O3"
%endif

#############################################################################

EXTRA_CFLAG=$CFLAGS

# Customize your system architecture in ARCH_NAME
# "_IA32_" for i686, "_IA64_" for ia64, 
# "_X86_64_" for Opteron, "_EM64T_" for Intel EM64T
# "_PPC64_" for PowerPC 64
%ifarch i386
export ARCH="_IA32_"
if [ %{compiler} == "gcc" ]; then
    # Flag fixes for Fedora PPC
    CFLAGS="-m32 $CFLAGS"
    CXXFLAGS="-m32 $CXXFLAGS"
    CPPFLAGS="-m32 $CPPFLAGS"
    FFLAGS="-m32 $FFLAGS"
    F90FLAGS="-m32 $F90FLAGS"
    LDFLAGS="-m32 $LDFLAGS"
    USER_CFLAGS="-m32 $USER_CFLAGS"
    MPIRUN_CFLAGS="-m32 $MPIRUN_CFLAGS"
    MPE_FLAGS=-mpe_opts="--with-cflags=-m32 --with-fflags=-m32"
fi
%endif
%ifarch ia64
export ARCH="_IA64_"
if [[ (( -f /lib/ssa/libgcc_s.so ) || ( -f /usr/lib/libgcc_s.so )) ]]; then
    EXTRA_CFLAG=" -L/lib/ssa -L/usr/lib -lgcc_s"
fi
%endif
%ifarch ppc64
export ARCH="_PPC64_"
if [ %{compiler} == "gcc" ]; then
    # Flag fixes for Fedora PPC
    CFLAGS="-m64 $CFLAGS"
    CXXFLAGS="-m64 $CXXFLAGS"
    CPPFLAGS="-m64 $CPPFLAGS"
    FFLAGS="-m64 $FFLAGS"
    F90FLAGS="-m64 $F90FLAGS"
    LDFLAGS="-m64 $LDFLAGS"
    USER_CFLAGS="-m64 $USER_CFLAGS"
    MPIRUN_CFLAGS="-m64 $MPIRUN_CFLAGS"
    MPE_FLAGS=-mpe_opts="--with-cflags=-m64 --with-fflags=-m64"
fi
%endif
%ifarch x86_64
export ARCH="_X86_64_"
if [ %{compiler} == "gcc" ]; then
    # Flag fixes for Fedora PPC
    CFLAGS="-m64 $CFLAGS"
    CXXFLAGS="-m64 $CXXFLAGS"
    CPPFLAGS="-m64 $CPPFLAGS"
    FFLAGS="-m64 $FFLAGS"
    F90FLAGS="-m64 $F90FLAGS"
    LDFLAGS="-m64 $LDFLAGS"
    USER_CFLAGS="-m64 $USER_CFLAGS"
    MPIRUN_CFLAGS="-m64 $MPIRUN_CFLAGS"
    MPE_FLAGS=-mpe_opts="--with-cflags=-m64 --with-fflags=-m64"
fi
%endif

# check for version
if [ -f $buildidfile ]; then
    buildid=`cat $buildidfile | grep MVAPICH_BUILDID |awk '{print $2}'`
    if [ "$buildid" != "" ];then
        DEF_BUILDID="$DEF_BUILDID -DMVAPICH_BUILDID=\\\"$buildid\\\""
    else
        DEF_BUILDID=""
    fi
fi

# Must set these in order to keep configure from breaking
export IB_HOME=/usr
export IB_HOME_LIB=%{_libdir}
export PREFIX=%{mpidir}
export COMPAT=COMPAT_MODE
# end required settings
export RSHCOMMAND=ssh
TMP_CFLAGS="$CFLAGS"
export CFLAGS="$TMP_CFLAGS -D$ARCH $OPTIMIZATION_FLAG -g -D_GNU_SOURCE -DCH_GEN2 -D_AFFINITY_ -DMEMORY_SCALE -D_SMP_ -D_SMP_RNDV_ -DVIADEV_RPUT_SUPPORT -DEARLY_SEND_COMPLETION"
export USER_CFLAGS
export MPE_OPTS
export MPE_CFLAGS
export LDFLAGS
export CXXFLAGS="$CXXFLAGS"
export FFLAGS="$FFLAGS $EXTRA_CFLAG"
export F90FLAGS="$F90FLAGS $EXTRA_CFLAG"
export CONFIG_FLAGS
export MPIRUN_CFLAGS="$MPIRUN_CFLAGS -DPARAM_GLOBAL=\\\"%{_sysconfidr}/%{namearch}/$conffile\\\" -DLD_LIBRARY_PATH_MPI=\\\"%{mpidir}/lib\\\" -DMPI_PREFIX=\\\"%{mpidir}/\\\" $DEF_BUILDID"
set -o pipefail
./configure --enable-sharedlib=%{mpidir}/lib --with-device=%{mpi_device} --with-mpd --with-arch=LINUX -prefix=%{mpidir} --with-echo $CONFIG_ENABLE_F77 $CONFIG_ENABLE_F90 $COMPILER_CONFIG -lib="-libverbs -libumad -lpthread $EXTRA_CFLAG" $MPE_FLAGS $CONFIG_FLAGS
%ifarch x86_64
cd ../.psm
export PREFIX=%{mpipsmdir}
export MPIRUN_CFLAGS="$MPIRUN_CFLAGS -DPARAM_GLOBAL=\\\"%{_sysconfidr}/%{namepsmarch}/$conffile\\\" -DLD_LIBRARY_PATH_MPI=\\\"%{mpipsmdir}/lib\\\" -DMPI_PREFIX=\\\"%{mpipsmdir}/\\\" $DEF_BUILDID"
export CFLAGS="$TMP_CFLAGS -D$ARCH $OPTIMIZATION_FLAG -g -D_GNU_SOURCE -DCH_PSM -D_AFFINITY_ -DMEMORY_SCALE -D_SMP_ -D_SMP_RNDV_ -DVIADEV_RPUT_SUPPORT -DEARLY_SEND_COMPLETION"
./configure --enable-sharedlib=%{mpipsmdir}/lib --with-device=ch_psm \
 --with-mpd --with-arch=LINUX -prefix=%{mpipsmdir} --with-echo $CONFIG_ENABLE_F77\
 $CONFIG_ENABLE_F90 $COMPILER_CONFIG -lib="-lpthread -lpsm_infinipath\
 $EXTRA_CFLAG" --without-mpe $CONFIG_FLAGS
%endif

%build
# We found that the mvapich2 make system does smp unsafe things (at least when
# doing smp makes over NFS), so use a non-smp make here too just for safety
cd .non-psm
make
%ifarch x86_64
cd ../.psm
make
%endif

%install
rm -rf %{buildroot}
cd .non-psm
make DESTDIR=%{buildroot} install 

# Post install fixes
# Remove bad links
rm -f %{buildroot}%{mpidir}/share/examples/mpirun
# Remove the uninstall script
rm -f %{buildroot}%{mpidir}/sbin/mpiuninstall
# Change and enable some defaults in mvapich.conf
perl -pi -e "s,^# VIADEV_DEFAULT_MIN_RNR_TIMER=12,VIADEV_DEFAULT_MIN_RNR_TIMER=25,g" %{buildroot}%{mpidir}/etc/mvapich.conf

# Move some files around to comply with Fedora MPI guidelines
mkdir -p %{buildroot}%{_mandir}/%{namearch}
mv %{buildroot}%{mpidir}/man/* %{buildroot}%{_mandir}/%{namearch}
find %{buildroot}%{_mandir}/%{namearch}/man1 -name \*.1 | xargs gzip -9
find %{buildroot}%{_mandir}/%{namearch}/man3 -name \*.3 | xargs gzip -9
find %{buildroot}%{_mandir}/%{namearch}/man4 -name \*.4 | xargs gzip -9
rmdir %{buildroot}%{mpidir}/man
mkdir %{buildroot}%{_mandir}/%{namearch}/man{2,5,6,7,8,9,n}

mv %{buildroot}%{mpidir}/sbin/* %{buildroot}%{mpidir}/bin
rmdir %{buildroot}%{mpidir}/sbin

rm -fr %{buildroot}%{mpidir}/share
rm -fr %{buildroot}%{mpidir}/doc
rm -fr %{buildroot}%{mpidir}/www
rm -fr %{buildroot}%{mpidir}/examples

mkdir -p %{buildroot}%{python_sitearch}/%{name}%{?_cc_name_suffix}
mkdir -p %{buildroot}%{_fmoddir}/%{namearch}

install -m644 -D %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm/macros.%{namearch}

mkdir -p %{buildroot}%{_sysconfdir}/modulefiles
sed 's#@LIBDIR@#'%{_libdir}/%{name}'#g;s#@ETCDIR@#'%{_sysconfdir}/%{namearch}'#g;s#@FMODDIR@#'%{_fmoddir}/%{namearch}'#g;s#@INCDIR@#'%{_includedir}/%{namearch}'#g;s#@MANDIR@#'%{_mandir}/%{namearch}'#g;s#@PYSITEARCH@#'%{python_sitearch}/%{name}'#g;s#@COMPILER@#%{name}-'%{_arch}%{?_cc_name_suffix}'#g;s#@SUFFIX@#'%{?_cc_name_suffix}'_%{name}#g' < %{SOURCE2} > %{buildroot}%{_sysconfdir}/modulefiles/%{namearch}
%ifarch x86_64
cd ../.psm
make DESTDIR=%{buildroot} install 

# Post install fixes
# Remove bad links
rm -f %{buildroot}%{mpipsmdir}/share/examples/mpirun
# Remove the uninstall script
rm -f %{buildroot}%{mpipsmdir}/sbin/mpiuninstall
# Change and enable some defaults in mvapich.conf
perl -pi -e "s,^# VIADEV_DEFAULT_MIN_RNR_TIMER=12,VIADEV_DEFAULT_MIN_RNR_TIMER=25,g" %{buildroot}%{mpipsmdir}/etc/mvapich.conf

# Move some files around to comply with Fedora MPI guidelines
mkdir -p %{buildroot}%{_mandir}/%{namepsmarch}
mv %{buildroot}%{mpipsmdir}/man/* %{buildroot}%{_mandir}/%{namepsmarch}
find %{buildroot}%{_mandir}/%{namepsmarch}/man1 -name \*.1 | xargs gzip -9
find %{buildroot}%{_mandir}/%{namepsmarch}/man3 -name \*.3 | xargs gzip -9
find %{buildroot}%{_mandir}/%{namepsmarch}/man4 -name \*.4 | xargs gzip -9
rmdir %{buildroot}%{mpipsmdir}/man
mkdir %{buildroot}%{_mandir}/%{namepsmarch}/man{2,5,6,7,8,9,n}

mv %{buildroot}%{mpipsmdir}/sbin/* %{buildroot}%{mpipsmdir}/bin
rmdir %{buildroot}%{mpipsmdir}/sbin

rm -fr %{buildroot}%{mpipsmdir}/share
rm -fr %{buildroot}%{mpipsmdir}/doc
rm -fr %{buildroot}%{mpipsmdir}/www
rm -fr %{buildroot}%{mpipsmdir}/examples

install -m644 -D %{SOURCE3} %{buildroot}%{_sysconfdir}/rpm/macros.%{namepsmarch}

sed 's#@LIBDIR@#'%{_libdir}/%{name}'#g;s#@ETCDIR@#'%{_sysconfdir}/%{namepsmarch}'#g;s#@FMODDIR@#'%{_fmoddir}/%{namepsmarch}'#g;s#@INCDIR@#'%{_includedir}/%{namepsmarch}'#g;s#@MANDIR@#'%{_mandir}/%{namepsmarch}'#g;s#@PYSITEARCH@#'%{python_sitearch}/%{name}'#g;s#@COMPILER@#%{name}-'%{_arch}%{?_cc_name_suffix}'#g;s#@SUFFIX@#'%{?_cc_name_suffix}'_%{name}#g' < %{SOURCE2} > %{buildroot}%{_sysconfdir}/modulefiles/%{namepsmarch}
%endif

%clean
rm -rf %{buildroot}

%post

%preun

%files
%defattr(-, root, root, -)
%dir %{mpidir}
%{mpidir}/*
%dir %{_mandir}/%{namearch}
%{_mandir}/%{namearch}/mandesc
%dir %{_mandir}/%{namearch}/man?
%{_mandir}/%{namearch}/man1/*
%{_sysconfdir}/modulefiles/*
%dir %{python_sitearch}/*
%dir %{_fmoddir}/*
%exclude %{mpidir}/lib/*.a
%exclude %{mpidir}/lib/*.so
%exclude %{mpidir}/include
%exclude %{mpidir}/bin/mpicc
%exclude %{mpidir}/bin/mpiCC
%exclude %{mpidir}/bin/mpicxx

%files devel
%defattr(-, root, root, -)
%{_mandir}/%{namearch}/man[34]/*
%{_sysconfdir}/rpm/*
%{mpidir}/lib/*.so
%dir %{mpidir}/include
%{mpidir}/include/*
%{mpidir}/bin/mpicc
%{mpidir}/bin/mpiCC
%{mpidir}/bin/mpicxx

%files common
%defattr(-, root, root, -)
%doc BUILDID CHANGELOG COPYRIGHT* INSTALL LICENSE.TXT README* doc examples www* share installtest

%files static
%defattr(-, root, root, -)
%{mpidir}/lib/*.a

%ifarch x86_64
%files psm
%defattr(-, root, root, -)
%dir %{mpipsmdir}
%{mpipsmdir}/*
%dir %{_mandir}/%{namepsmarch}
%{_mandir}/%{namepsmarch}/mandesc
%dir %{_mandir}/%{namepsmarch}/man?
%{_mandir}/%{namepsmarch}/man1/*
%{_sysconfdir}/modulefiles/*
%dir %{python_sitearch}/*
%dir %{_fmoddir}/*
%exclude %{mpipsmdir}/lib/*.a
%exclude %{mpipsmdir}/lib/*.so
%exclude %{mpipsmdir}/include
%exclude %{mpipsmdir}/bin/mpicc
%exclude %{mpipsmdir}/bin/mpiCC
%exclude %{mpipsmdir}/bin/mpicxx

%files psm-devel
%defattr(-, root, root, -)
%{_mandir}/%{namepsmarch}/man[34]/*
%{_sysconfdir}/rpm/*
%{mpipsmdir}/lib/*.so
%dir %{mpipsmdir}/include
%{mpipsmdir}/include/*
%{mpipsmdir}/bin/mpicc
%{mpipsmdir}/bin/mpiCC
%{mpipsmdir}/bin/mpicxx

%files psm-static
%defattr(-, root, root, -)
%{mpipsmdir}/lib/*.a
%endif

%changelog
* Fri Jun 4 2010 Jay Fenlason <fenlason@redhat.com> 1.2.0-0.3562.5.el6
- Reorganization and stuff to build -psm packages on x86_64 (only)
  Related: rhbz570274

* Tue Mar 2 2010 Jay Fenlason <fenlason@redhat.com> 1.2.0-0.3562.4.el6
- Move -devel subpackages requires to the devel subpackage.
  Resolves: bz568439

* Fri Jan 15 2010 Doug Ledford <dledford@redhat.com> - 1.2.0-0.3562.3.el6
- Fix an issue with usage of _cc_name_suffix that caused a broken define in
  our module file
- Related: bz543948

* Fri Jan 15 2010 Doug Ledford <dledford@redhat.com> - 1.2.0-0.3562.2.el6
- Forward port to the Fedora MPI packaging guidelines and build for
  Red Hat Enterprise Linux 6
- Related: bz543948

* Tue Dec 22 2009 Doug Ledford <dledford@redhat.com> - 1.2.0-0.3562.1.el5
- Update to latest upstream version
- Related: bz518218

* Mon Jun 22 2009 Doug Ledford <dledford@redhat.com> - 1.1.0-0.3355.2.el5
- Rebuild against libibverbs that isn't missing the proper ppc wmb() macro
- Related: bz506258

* Sun Jun 21 2009 Doug Ledford <dledford@redhat.com> - 1.1.0-0.3355.1.el5
- Update to final ofed 1.4.1 bits
- Compile against non-XRC libibverbs
- Related: bz506258, bz506097

* Wed Apr 22 2009 Doug Ledford <dledford@redhat.com> - 1.1.0-0.3143.1
- Update to ofed 1.4.1-rc3 version
- Related: bz459652

* Thu Oct 16 2008 Doug Ledford <dledford@redhat.com> - 1.1.0-0.2931.3
- The mpivars files needed the shared library directory updated
- Resolves: bz466389

* Fri Oct 03 2008 Doug Ledford <dledford@redhat.com> - 1.1.0-0.2931.2
- Incorporate fixups to Requires(post) and Requires(preun) from openmpi
- Fix up post/preun scripts to work like the scripts from openmpi11
- Resolves: bz465448

* Thu Sep 18 2008 Doug Ledford <dledford@redhat.com> - 1.1.0-0.2931.1
- Rearrange the position of the svn tag in the n-v-r so z stream updates
  won't be so ugly should they ever be needed

* Wed Sep 17 2008 Doug Ledford <dledford@redhat.com> - 1.1.0-0.el5.2931.1
- Update to later upstream source, gut spec file and make it sane
- Resolves: bz451476

* Mon May  12 2008 Pavel Shamis <pasha@mellanox.co.il>
- Fixes for mvapich 1.1 and OFED 1.4:
* Mon May  12 2008 Pavel Shamis <pasha@mellanox.co.il>
- Adding SUN compiler support
- Adding -fPIC to Pathscale, GCC and Intel
* Sun May  4 2008 Pavel Shamis <pasha@mellanox.co.il>
- Removing unused code
* Mon Jan  7 2008 Pavel Shamis <pasha@mellanox.co.il>
- Enable F90 build on PPC platforms
* Thu Dec  6 2007 Pavel Shamis <pasha@mellanox.co.il>
- Adding -fPIC compilation flag for pgi compiler
* Mon Dec  5 2007 Pavel Shamis <pasha@mellanox.co.il>
- Removing explicit Provides
- Replacing autoreqprov autoreq
* Mon Dec  3 2007 Pavel Shamis <pasha@mellanox.co.il>
- Fixing PGI 7.1 failure
* Wed Oct 31 2007 Pavel Shamis <pasha@mellanox.co.il>
- Adding support for mvapich 1.0.0 version
- Fixing mpi-selector bug
* Wed Aug 12 2007 Pavel Shamis <pasha@mellanox.co.il>
- Replacing default mvapich tunings with new values.
* Wed Jun  6 2007 Pavel Shamis <pasha@mellanox.co.il>
- Fixed PGI build bug. PGI doesn't support -Wall flag.
* Sun Mar 25 2007 Pavel Shamis <pasha@mellanox.co.il>
- Added support for mpi_compat_mode. 
* Wed Mar  8 2007 Pavel Shamis <pasha@mellanox.co.il>
- Intel compiler name was changed from icc to intel
* Tue Mar  6 2007 Pavel Shamis <pasha@mellanox.co.il>
- Fixed bug in mvapich.sh/csh generation.
* Thu Mar  1 2007 Pavel Shamis <pasha@mellanox.co.il>
- OFED section was moved before rpm definition section.
* Thu Mar  1 2007 Pavel Shamis <pasha@mellanox.co.il>
- OFED section was moved before rpm definition section.
* Thu Feb 20 2007 Pavel Shamis <pasha@mellanox.co.il>
- added support for mpi-selector
* Mon Feb  5 2007 Pavel Shamis <pasha@mellanox.co.il>
- the %build macro was removed,workaround for SUSE issue - %build removes $RPM_BUILD_ROOT
- added "-libcommon" for SuSe10
* Tue Jan 30 2007 Pavel Shamis <pasha@mellanox.co.il>
- The spec file was created
