package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
)

const ROOT_DIR = "./webdir/"

func enum_dir(path string) []os.FileInfo {
	if files, err := ioutil.ReadDir(path); err == nil {
		return files
	} else {
		return []os.FileInfo{}
	}
}

func read_file(base string, name string) string {
	if strings.Contains(strings.ToLower(name), "flag_file.txt") || strings.ContainsAny(name, "/") {
		return "forbidden!"
	}

	if content, err := ioutil.ReadFile(base + name); err == nil {
		return string(content)
	} else {
		return "error!"
	}
}

func handle_list(w http.ResponseWriter, r *http.Request) {
	if templ, err := template.ParseFiles("./list.gohtml"); err == nil {
		templ.Execute(w, enum_dir(ROOT_DIR))
	} else {
		fmt.Fprintf(w, "Error! err=%s", err)
	}
}

func handle_show(w http.ResponseWriter, r *http.Request) {
	values, err := url.ParseQuery(r.URL.RawQuery)
	if err != nil {
		fmt.Fprintf(w, "Error! err=%s", err)
		return
	}

	path := values.Get("path")

	if templ, err := template.ParseFiles("./show.gohtml"); err == nil {
		templ.Execute(w, read_file(ROOT_DIR, path))
	} else {
		fmt.Fprintf(w, "Error! err=%s", err)
	}
}

func main() {
	http.HandleFunc("/", handle_list)
	http.HandleFunc("/show", handle_show)
	println("Starting and listening on :1024...")
	log.Fatal(http.ListenAndServe(":1024", nil))
}
