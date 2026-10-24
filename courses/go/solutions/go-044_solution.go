package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Rule struct {
	Namespace, Resource string
	Verbs               []string
}

func allowed(r Rule, namespace, resource, verb string) bool {
	if r.Namespace != namespace || r.Resource != resource {
		return false
	}
	for _, v := range r.Verbs {
		if v == verb {
			return true
		}
	}
	return false
}

func main() {
	// Admit a required read
	{
		rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}
		check(allowed(rule, "lesson", "pods", "get"), "read")
	}

	// Reject an unneeded mutation
	{
		rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
		check(!allowed(rule, "lesson", "pods", "delete"), "mutation")
	}

	// Reject cross-namespace access
	{
		rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
		check(!allowed(rule, "other", "pods", "get"), "namespace")
	}

	// Separate resource and subresource
	{
		rule := Rule{Namespace: "lesson", Resource: "deployments/status", Verbs: []string{"update"}}
		check(allowed(rule, "lesson", "deployments/status", "update") && !allowed(rule, "lesson", "deployments", "update"), "subresource")
	}

	// Treat secret reads as authority
	{
		rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
		check(!allowed(rule, "lesson", "secrets", "get"), "secret boundary")
	}

	// Transfer verb distinction
	{
		rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"list"}}
		check(allowed(rule, "lesson", "pods", "list") && !allowed(rule, "lesson", "pods", "watch"), "verbs")
	}
	fmt.Println("All lesson checks passed.")
}
