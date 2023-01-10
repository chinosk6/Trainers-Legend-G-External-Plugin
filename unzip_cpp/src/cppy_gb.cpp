#include <pybind11/pybind11.h>
#include <iostream>
#include <filesystem>
#include <fstream>

#include "bitextractor.hpp"
#include "bitexception.hpp"
#include "resize_window.hpp"

using namespace bit7z;
namespace py = pybind11;
using namespace py::literals;

class UnzipZip {
public:
	UnzipZip(const std::string& data) : wuhu(data) {
		printf("俺の愛馬が！\n");
	}
    std::string wuhu;

    static std::string decompress_file(std::string zipname, std::string outputPath)
    {
        try {

            std::wstring filename{ zipname.begin(), zipname.end() };
            std::wstring outPath{ outputPath.begin(), outputPath.end() };

            Bit7zLibrary lib{ L"7z.dll" };
            BitExtractor extractor{ lib, BitFormat::Zip };

            if (!std::filesystem::exists(outPath)) {
                std::filesystem::create_directories(outPath);
            }
            extractor.extract(filename, outPath);
            return "ok";
        }
        catch (const BitException& ex) {
            return std::format("UnzipError: {}", ex.what());
        }
    }
};


PYBIND11_MODULE(umauitools, m) {
    m.doc() = "wohaoxianghemayazuoai!";

    py::class_<UnzipZip>(m, "Unzip")
        .def(py::init<const std::string&>())
        .def("decompress_file", &UnzipZip::decompress_file)
		.def_readwrite("wuhu", &UnzipZip::wuhu)
        ;

    py::class_<WindowResize>(m, "WindowController")
        .def(py::init<const std::string&>())
        .def("setClassName", &WindowResize::setClassName)
        .def("getWindow", &WindowResize::getWindow)
        .def("setWindowPosOffset", &WindowResize::setWindowPosOffset)
        .def("moveWindowPosOffset", &WindowResize::moveWindowPosOffset)
        .def("moveWindow", &WindowResize::moveWindow)
        .def("getWindowPos", &WindowResize::getWindowPos)
        .def("resizeWindow", &WindowResize::resizeWindow)
        .def_readwrite("classsName", &WindowResize::classsName)
        .def_readwrite("windowName", &WindowResize::windowName)
        ;
}
