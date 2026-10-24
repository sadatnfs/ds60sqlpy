package main

import (
	"encoding/json"
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Metadata struct {
	Name      string `json:"name"`
	Namespace string `json:"namespace"`
	UID       string `json:"uid"`
	Version   string `json:"resourceVersion"`
}
type Deployment struct {
	APIVersion string   `json:"apiVersion"`
	Kind       string   `json:"kind"`
	Metadata   Metadata `json:"metadata"`
	Spec       struct {
		Replicas *int `json:"replicas"`
	} `json:"spec"`
	Status struct {
		Ready int `json:"readyReplicas"`
	} `json:"status"`
}

func main() {
	// Decode desired and observed replicas
	{
		var d Deployment
		err := json.Unmarshal([]byte(`{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"demo","namespace":"lesson","uid":"u1"},"spec":{"replicas":3},"status":{"readyReplicas":2}}`), &d)
		check(err == nil && d.Spec.Replicas != nil && *d.Spec.Replicas == 3 && d.Status.Ready == 2, "spec status")
	}

	// Distinguish omitted from explicit zero
	{
		var a, b Deployment
		check(json.Unmarshal([]byte(`{"spec":{}}`), &a) == nil, "decode")
		check(json.Unmarshal([]byte(`{"spec":{"replicas":0}}`), &b) == nil, "decode")
		check(a.Spec.Replicas == nil && b.Spec.Replicas != nil && *b.Spec.Replicas == 0, "presence")
	}

	// Separate name and incarnation
	{
		a := Metadata{Name: "demo", Namespace: "lesson", UID: "old"}
		b := Metadata{Name: "demo", Namespace: "lesson", UID: "new"}
		check(a.Name == b.Name && a.UID != b.UID, "incarnation")
	}

	// Keep namespaces in a key
	{
		a, b := "alpha/demo", "beta/demo"
		check(a != b, "namespace key")
	}

	// Treat versions as opaque
	{
		m := Metadata{Version: "opaque-v7"}
		check(m.Version == "opaque-v7", "opaque version")
	}

	// Transfer readiness reasoning
	{
		wanted := 3
		check(wanted == 3 && 3 == wanted, "ready")
		check(2 != wanted, "not ready")
	}
	fmt.Println("All lesson checks passed.")
}
