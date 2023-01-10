#pragma once
#include <string>
#include <Windows.h>
#include <memory>
#include <format>


class WindowResize {
public:
	std::string classsName;
	std::string windowName;

	WindowResize(const std::string& windowName){
		this->classsName = "UMA_NULL_0F3AB7D9";
		this->windowName = windowName;
	}

	void setClassName(const std::string& classsName) {
		this->classsName = classsName;
	}

	HWND getWindow() {
		LPCSTR _className = this->classsName == "UMA_NULL_0F3AB7D9" ? NULL : this->classsName.c_str();
		return FindWindowA(_className, this->windowName.c_str());
	}

	bool setWindowPosOffset(HWND hWnd, HWND hWndInsertAfter, int X, int Y, int cx, int cy, UINT uFlags) {
		std::shared_ptr<RECT> windowR = std::make_shared<RECT>();
		std::shared_ptr<RECT> clientR = std::make_shared<RECT>();
		GetWindowRect(hWnd, windowR.get());
		GetClientRect(hWnd, clientR.get());
		return SetWindowPos(hWnd, hWndInsertAfter, X, Y, cx + windowR->right - windowR->left - clientR->right,
			cy + windowR->bottom - windowR->top - clientR->bottom, uFlags);
	}

	bool moveWindowPosOffset(HWND hWnd, LPRECT windowR, int X, int Y) {
		std::shared_ptr<RECT> clientR = std::make_shared<RECT>();
		GetClientRect(hWnd, clientR.get());
		return SetWindowPos(hWnd, HWND_NOTOPMOST, X, Y,
			windowR->right - windowR->left, windowR->bottom - windowR->top, SWP_DEFERERASE);
	}

	bool moveWindow(int move_x, int move_y) {
		auto window = getWindow();
		if (window == NULL) return false;
		std::shared_ptr<RECT> windowR = std::make_shared<RECT>();
		GetWindowRect(window, windowR.get());
		int x = windowR->left + move_x;
		int y = windowR->top + move_y;
		return moveWindowPosOffset(window, windowR.get(), x, y);
	}

	std::string getWindowPos() {
		auto window = getWindow();
		if (window == NULL) return "";
		std::shared_ptr<RECT> windowR = std::make_shared<RECT>();
		std::shared_ptr<RECT> clientR = std::make_shared<RECT>();
		GetWindowRect(window, windowR.get());
		GetClientRect(window, clientR.get());
		return std::format("{},{},{},{}", windowR->left, windowR->top, clientR->right - clientR->left, clientR->bottom - clientR->top);
	}

	bool resizeWindow(int x, int y, int w, int h) {
		auto window = getWindow();
		if (window == NULL) return false;
		return setWindowPosOffset(window, HWND_NOTOPMOST, x, y, w, h, SWP_DEFERERASE);
	}
};
