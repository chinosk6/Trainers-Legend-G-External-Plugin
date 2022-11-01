#include <pybind11/pybind11.h>
#include <iostream>
#include <minizip/unzip.h>
#include <filesystem>
#include <fstream>
// #include <pybind11/numpy.h>

namespace py = pybind11;
using namespace py::literals;

class UnzipZip {
public:
	UnzipZip(const std::string& data) : wuhu(data) {
		printf("俺の愛馬が！\n");
	}

	static std::string decompress_file(const std::string updateFile, const std::string tmPath)
	{
		const std::filesystem::path tmpPath = tmPath;
		const auto zipFile = unzOpen(updateFile.c_str());
		if (!zipFile)
		{
			return "Cannot open update file, updating interrupted";
		}

		unz_global_info info;
		if (unzGetGlobalInfo(zipFile, &info) != UNZ_OK)
		{
			return "Cannot get update file zip info, updating interrupted";
		}

		constexpr std::size_t BufferSize = 1024;
		char buffer[BufferSize];

		for (std::size_t i = 0; i < info.number_entry; ++i)
		{
			unz_file_info fileInfo;
			if (unzGetCurrentFileInfo(zipFile, &fileInfo, buffer, BufferSize, nullptr, 0, nullptr, 0) != UNZ_OK)
			{
				return "Cannot get update file entry info, updating interrupted";
			}

			const std::string_view fileNameView(buffer, fileInfo.size_filename);
			buffer[fileInfo.size_filename] = '\0';
			// std::printf("Entry name: %s, ", buffer);

			if (unzOpenCurrentFile(zipFile) != UNZ_OK)
			{
				return "Cannot open current update file entry, updating interrupted";
			}
			const std::filesystem::path filePath = tmpPath / fileNameView;
			if (filePath.native().ends_with(L"/"))
			{
				std::filesystem::create_directories(filePath);
			}
			else
			{
				std::filesystem::create_directories(filePath.parent_path());
				std::ofstream output(filePath, std::ios::binary);
				if (!output.is_open())
				{
					return "Cannot open update file entry, updating interrupted";
				}
				int readSizeOrError;
				// 循环开始时不能继续使用 fileNameView，已被复用于文件内容缓存
				do
				{
					readSizeOrError = unzReadCurrentFile(zipFile, buffer, BufferSize);
					if (readSizeOrError < 0)
					{
						return "Cannot read current update file entry, updating interrupted";
					}
					output.write(buffer, readSizeOrError);
				} while (readSizeOrError != 0);
			}


			unzCloseCurrentFile(zipFile);

			if (i + 1 != info.number_entry && unzGoToNextFile(zipFile) != UNZ_OK)
			{
				return "Cannot iterate update file entry, updating interrupted";
			}
		}
		unzClose(zipFile);
		return "ok";
	}

	std::string wuhu;
};


PYBIND11_MODULE(umauitools, m) {
    m.doc() = "wohaoxianghemayazuoai!";

    py::class_<UnzipZip>(m, "Unzip")
        .def(py::init<const std::string&>())
        .def("decompress_file", &UnzipZip::decompress_file)
		.def_readwrite("wuhu", &UnzipZip::wuhu)
        ;
}

