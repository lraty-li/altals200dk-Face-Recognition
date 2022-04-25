package handlers

import (
	"html/template"
	"io"
	"net/http"
)

func FaceSign(writer http.ResponseWriter, request *http.Request) {

	isLogin := ifLogined(writer, request)

	if isLogin {
		//authed
		t, _ := template.ParseFiles("template/faceSign.html")
		_ = t.Execute(writer, nil)
		// generateHTML(writer, threads, "layout", "auth.navbar", "index")

	} else {
		//need login
		t, _ := template.ParseFiles("template/login.html")
		_ = t.Execute(writer, nil)
	}
}

func FaceSignGetIC(writer http.ResponseWriter, request *http.Request) {
	io.WriteString(writer, "123456")
}

func FaceSignAccount(writer http.ResponseWriter, request *http.Request) {

}

func preProgress() {
	//TODO 显示注册结果
	//face img to vator

}
