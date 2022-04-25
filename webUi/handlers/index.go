package handlers

import (
	"html/template"
	"net/http"
)

func Index(writer http.ResponseWriter, request *http.Request) {
	isLogin := ifLogined(writer, request)

	if isLogin {
		//authed
		t, _ := template.ParseFiles("template/index.html")
		_ = t.Execute(writer, nil)
		// generateHTML(writer, threads, "layout", "auth.navbar", "index")

	} else {
		//need login
		t, _ := template.ParseFiles("template/login.html")
		_ = t.Execute(writer, nil)
	}
}

func Err(writer http.ResponseWriter, request *http.Request) {
	vals := request.URL.Query()
	_, err := session(writer, request)
	if err != nil {
		generateHTML(writer, vals.Get("msg"), "layout", "navbar", "error")
	} else {
		generateHTML(writer, vals.Get("msg"), "layout", "auth.navbar", "error")
	}
}
