package main

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func validateTarget(endpoint, namespace, contextName string) error {
	u, err := url.Parse(endpoint)
	if err != nil || u.Scheme != "https" || u.Host == "" || u.User != nil {
		return errors.New("explicit HTTPS endpoint required")
	}
	if namespace == "" || strings.ContainsAny(namespace, "/\\ ") || contextName == "" {
		return errors.New("explicit namespace and context required")
	}
	return nil
}

func main() {
	// Accept explicit secure configuration
	{
		check(validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil, "target")
	}

	// Reject insecure transport
	{
		check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") != nil, "TLS")
	}

	// Reject ambient context selection
	{
		check(validateTarget("https://cluster.invalid", "lesson", "") != nil, "explicit context")
	}

	// Constrain a namespace
	{
		check(validateTarget("https://cluster.invalid", "lesson/other", "owned") != nil, "namespace")
	}

	// Construct a bounded request
	{
		req, err := http.NewRequestWithContext(context.Background(), "GET", "https://cluster.invalid/api/v1/namespaces/lesson/pods?limit=20", nil)
		check(err == nil && req.Method == "GET" && req.URL.Path == "/api/v1/namespaces/lesson/pods", "request")
	}

	// Transfer userinfo rejection
	{
		target := url.URL{Scheme: "https", Host: "cluster.invalid", User: url.UserPassword("sample-user", "sample-value")}
		check(validateTarget(target.String(), "lesson", "owned") != nil, "userinfo")
	}
	fmt.Println("All lesson checks passed.")
}
