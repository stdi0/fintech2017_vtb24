package main

import (
	"net/http"
	"log"
	"html/template"
)

func request_code(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {

	}
	tmpl, err := template.ParseFiles("form.html")
	if err != nil {
		log.Println("Can not expand template", err)
		return
	}
	err = tmpl.Execute(w, nil)
	if err != nil {
		log.Println(err)
	}
} 

func main() {
	port := "5000"
	http.HandleFunc("/sms", request_code)
	http.ListenAndServe("67.205.176.154:"+port, nil)
	return
}
