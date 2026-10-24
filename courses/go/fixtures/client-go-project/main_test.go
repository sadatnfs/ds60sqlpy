package main

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	corev1 "k8s.io/client-go/kubernetes/typed/core/v1"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	clientcmdapi "k8s.io/client-go/tools/clientcmd/api"
)

func TestNoAmbientConfiguration(t *testing.T) {
	if _, err := checkedConfig(options{}); err == nil {
		t.Fatal("empty configuration must fail before any ambient discovery")
	}
}

func TestTypedClientPagination(t *testing.T) {
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		if r.URL.Path != "/api/v1/namespaces/lesson/pods" || r.URL.Query().Get("limit") != "20" {
			t.Errorf("unexpected request path or page limit: %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		if calls == 1 {
			fmt.Fprint(w, `{"apiVersion":"v1","kind":"PodList","metadata":{"continue":"next"},"items":[{"metadata":{"name":"alpha"}}]}`)
		} else {
			if r.URL.Query().Get("continue") != "next" {
				t.Error("continuation token was not preserved")
			}
			fmt.Fprint(w, `{"apiVersion":"v1","kind":"PodList","metadata":{},"items":[{"metadata":{"name":"beta"}}]}`)
		}
	}))
	defer server.Close()
	client, err := corev1.NewForConfig(&rest.Config{Host: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	names, err := listNames(context.Background(), client, "lesson")
	if err != nil || strings.Join(names, ",") != "alpha,beta" || calls != 2 {
		t.Fatalf("unexpected names=%v calls=%d error=%v", names, calls, err)
	}
}

func TestTypedClientRejectsUnboundedPagination(t *testing.T) {
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprint(w, `{"apiVersion":"v1","kind":"PodList","metadata":{"continue":"more"},"items":[]}`)
	}))
	defer server.Close()
	client, err := corev1.NewForConfig(&rest.Config{Host: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := listNames(context.Background(), client, "lesson"); err == nil || calls != 3 {
		t.Fatalf("expected bounded failure, got calls=%d error=%v", calls, err)
	}
}

func TestCanceledClientDoesNotRequest(t *testing.T) {
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		http.Error(w, "unexpected", 500)
	}))
	defer server.Close()
	client, err := corev1.NewForConfig(&rest.Config{Host: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := listNames(ctx, client, "lesson"); err == nil {
		t.Fatal("cancellation must remain visible")
	}
	if calls != 0 {
		t.Fatal("already canceled operation reached the server")
	}
}

func TestExplicitConfigurationBoundaries(t *testing.T) {
	tests := []struct {
		name      string
		mutate    func(*clientcmdapi.Config, *options)
		wantError bool
	}{
		{"selected context ignores ambient current context", func(c *clientcmdapi.Config, o *options) {}, false},
		{"missing execute acknowledgement", func(c *clientcmdapi.Config, o *options) { o.execute = false }, true},
		{"missing named context", func(c *clientcmdapi.Config, o *options) { o.contextName = "absent" }, true},
		{"endpoint mismatch", func(c *clientcmdapi.Config, o *options) { o.expectedServer = "https://other.invalid:6443" }, true},
		{"insecure TLS", func(c *clientcmdapi.Config, o *options) { c.Clusters["owned"].InsecureSkipTLSVerify = true }, true},
		{"configured proxy", func(c *clientcmdapi.Config, o *options) { c.Clusters["owned"].ProxyURL = "http://proxy.invalid" }, true},
		{"credential executable", func(c *clientcmdapi.Config, o *options) {
			c.AuthInfos["reader"].Exec = &clientcmdapi.ExecConfig{Command: "must-not-run"}
		}, true},
		{"impersonation", func(c *clientcmdapi.Config, o *options) { c.AuthInfos["reader"].Impersonate = "another-user" }, true},
		{"namespace path", func(c *clientcmdapi.Config, o *options) { o.namespace = "lesson/other" }, true},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			raw := clientcmdapi.NewConfig()
			raw.Clusters["owned"] = &clientcmdapi.Cluster{Server: "https://cluster.invalid:6443"}
			raw.AuthInfos["reader"] = &clientcmdapi.AuthInfo{Token: "synthetic-teaching-token"}
			raw.Contexts["owned-lesson"] = &clientcmdapi.Context{Cluster: "owned", AuthInfo: "reader", Namespace: "lesson"}
			raw.CurrentContext = "unrelated"
			configPath := filepath.Join(t.TempDir(), "lesson-config")
			o := options{config: configPath, contextName: "owned-lesson", namespace: "lesson", expectedServer: "https://cluster.invalid:6443", execute: true}
			tc.mutate(raw, &o)
			data, err := clientcmd.Write(*raw)
			if err != nil {
				t.Fatal(err)
			}
			if err := os.WriteFile(configPath, data, 0600); err != nil {
				t.Fatal(err)
			}
			cfg, err := checkedConfig(o)
			if (err != nil) != tc.wantError {
				t.Fatalf("error=%v wantError=%v", err, tc.wantError)
			}
			if err == nil {
				if cfg.Host != o.expectedServer || cfg.Proxy == nil {
					t.Fatal("explicit endpoint or direct routing was lost")
				}
				proxy, err := cfg.Proxy(&http.Request{})
				if err != nil || proxy != nil {
					t.Fatal("host proxy must not be inherited")
				}
			}
		})
	}
}
