package main

import (
	"fmt"
	"net/http"
	"net/http/httptest"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func health(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/health" {
		http.NotFound(w, r)
		return
	}
	if r.Method != "GET" {
		w.Header().Set("Allow", "GET")
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "ok")
}

func main() {
	// Serve a health request
	{
		r := httptest.NewRecorder()
		health(r, httptest.NewRequest("GET", "/health", nil))
		check(r.Code == 200 && r.Body.String() == "ok\n", "health")
	}

	// Reject an unsupported method
	{
		r := httptest.NewRecorder()
		health(r, httptest.NewRequest("POST", "/health", nil))
		check(r.Code == 405 && r.Header().Get("Allow") == "GET", "method")
	}

	// Reject an unknown route
	{
		r := httptest.NewRecorder()
		health(r, httptest.NewRequest("GET", "/missing", nil))
		check(r.Code == 404, "route")
	}

	// Check content metadata
	{
		r := httptest.NewRecorder()
		health(r, httptest.NewRequest("GET", "/health", nil))
		check(r.Header().Get("Content-Type") == "text/plain; charset=utf-8", "content type")
	}

	// Repeat without shared mutation
	{
		for i := 0; i < 2; i++ {
			r := httptest.NewRecorder()
			health(r, httptest.NewRequest("GET", "/health", nil))
			check(r.Code == 200 && r.Body.String() == "ok\n", "repeat")
		}
	}

	// Transfer query independence
	{
		r := httptest.NewRecorder()
		health(r, httptest.NewRequest("GET", "/health?probe=1", nil))
		check(r.Code == 200, "query separation")
	}
	fmt.Println("All lesson checks passed.")
}
