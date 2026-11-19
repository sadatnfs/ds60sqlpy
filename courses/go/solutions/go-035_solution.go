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
		var a, b Deployment
		errA := json.Unmarshal([]byte(`{"metadata":{"name":"demo","namespace":"lesson","uid":"old"}}`), &a)
		errB := json.Unmarshal([]byte(`{"metadata":{"name":"demo","namespace":"lesson","uid":"new"}}`), &b)
		check(errA == nil && errB == nil, "decode")
		check(a.Metadata.Name == b.Metadata.Name && a.Metadata.UID != b.Metadata.UID, "incarnation")
	}

	// Keep namespaces in a key
	{
		key := func(m Metadata) string { return m.Namespace + "/" + m.Name }
		a := Metadata{Name: "demo", Namespace: "alpha"}
		b := Metadata{Name: "demo", Namespace: "beta"}
		check(key(a) == "alpha/demo" && key(a) != key(b), "namespace key")
	}

	// Treat versions as opaque
	{
		var a, b Metadata
		errA := json.Unmarshal([]byte(`{"resourceVersion":"10"}`), &a)
		errB := json.Unmarshal([]byte(`{"resourceVersion":"9"}`), &b)
		check(errA == nil && errB == nil, "decode")
		check(a.Version == "10" && a.Version != b.Version && a.Version < b.Version, "opaque version")
	}

	// Transfer readiness reasoning
	{
		complete := func(d Deployment) bool { return d.Spec.Replicas != nil && d.Status.Ready == *d.Spec.Replicas }
		want := 3
		var d Deployment
		d.Spec.Replicas = &want
		d.Status.Ready = 3
		check(complete(d), "ready")
		d.Status.Ready = 2
		check(!complete(d), "not ready")
	}
	fmt.Println("All lesson checks passed.")
}
