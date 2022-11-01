#!lua
conan_build_type = "Release"
conan_arch = "x86_64"

conan_includedirs = {"C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d/include",
"C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d/include/minizip",
"C:/Users/Y7000/.conan/data/zlib/1.2.12/_/_/package/3fb49604f9c2f729b85ba3115852006824e72cab/include",
"C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5/include"}
conan_libdirs = {"C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d/lib",
"C:/Users/Y7000/.conan/data/zlib/1.2.12/_/_/package/3fb49604f9c2f729b85ba3115852006824e72cab/lib",
"C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5/lib"}
conan_bindirs = {"C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5/bin"}
conan_libs = {"minizip", "zlib", "bz2"}
conan_system_libs = {}
conan_defines = {"HAVE_BZIP2"}
conan_cxxflags = {}
conan_cflags = {}
conan_sharedlinkflags = {}
conan_exelinkflags = {}
conan_frameworks = {}

conan_includedirs_minizip = {"C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d/include",
"C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d/include/minizip"}
conan_libdirs_minizip = {"C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d/lib"}
conan_bindirs_minizip = {}
conan_libs_minizip = {"minizip"}
conan_system_libs_minizip = {}
conan_defines_minizip = {"HAVE_BZIP2"}
conan_cxxflags_minizip = {}
conan_cflags_minizip = {}
conan_sharedlinkflags_minizip = {}
conan_exelinkflags_minizip = {}
conan_frameworks_minizip = {}
conan_rootpath_minizip = "C:/Users/Y7000/.conan/data/minizip/1.2.11/_/_/package/153ff990bb7a331b443365f9878a3991adbdea9d"

conan_includedirs_zlib = {"C:/Users/Y7000/.conan/data/zlib/1.2.12/_/_/package/3fb49604f9c2f729b85ba3115852006824e72cab/include"}
conan_libdirs_zlib = {"C:/Users/Y7000/.conan/data/zlib/1.2.12/_/_/package/3fb49604f9c2f729b85ba3115852006824e72cab/lib"}
conan_bindirs_zlib = {}
conan_libs_zlib = {"zlib"}
conan_system_libs_zlib = {}
conan_defines_zlib = {}
conan_cxxflags_zlib = {}
conan_cflags_zlib = {}
conan_sharedlinkflags_zlib = {}
conan_exelinkflags_zlib = {}
conan_frameworks_zlib = {}
conan_rootpath_zlib = "C:/Users/Y7000/.conan/data/zlib/1.2.12/_/_/package/3fb49604f9c2f729b85ba3115852006824e72cab"

conan_includedirs_bzip2 = {"C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5/include"}
conan_libdirs_bzip2 = {"C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5/lib"}
conan_bindirs_bzip2 = {"C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5/bin"}
conan_libs_bzip2 = {"bz2"}
conan_system_libs_bzip2 = {}
conan_defines_bzip2 = {}
conan_cxxflags_bzip2 = {}
conan_cflags_bzip2 = {}
conan_sharedlinkflags_bzip2 = {}
conan_exelinkflags_bzip2 = {}
conan_frameworks_bzip2 = {}
conan_rootpath_bzip2 = "C:/Users/Y7000/.conan/data/bzip2/1.0.8/_/_/package/d16a91eadaaf5829b928b12d2f836ff7680d3df5"

function conan_basic_setup()
    configurations{conan_build_type}
    architecture(conan_arch)
    includedirs{conan_includedirs}
    libdirs{conan_libdirs}
    links{conan_libs}
    links{conan_system_libs}
    links{conan_frameworks}
    defines{conan_defines}
    bindirs{conan_bindirs}
end
