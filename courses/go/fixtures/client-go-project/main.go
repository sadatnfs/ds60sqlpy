// This prepared project is separate from the ordinary one-file classroom pad.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	corev1 "k8s.io/client-go/kubernetes/typed/core/v1"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

type options struct {
	config, contextName, namespace, expectedServer string
	execute                                        bool
}

func checkedConfig(o options) (*rest.Config, error) {
	if !o.execute || o.config == "" || o.contextName == "" || o.namespace == "" || o.expectedServer == "" {
		return nil, errors.New("explicit execute, kubeconfig, context, namespace and expected-server are required")
	}
	if strings.ContainsAny(o.namespace, "/\\ \t\n") {
		return nil, errors.New("namespace must be one explicit name")
	}
	expected, err := url.Parse(o.expectedServer)
	if err != nil || expected.Scheme != "https" || expected.Host == "" || expected.User != nil || expected.RawQuery != "" || expected.Fragment != "" {
		return nil, errors.New("expected-server must be an explicit HTTPS API endpoint")
	}
	raw, err := clientcmd.LoadFromFile(o.config)
	if err != nil {
		return nil, errors.New("cannot load the explicitly selected kubeconfig")
	}
	selected, ok := raw.Contexts[o.contextName]
	if !ok {
		return nil, errors.New("the explicit context is absent")
	}
	cluster, ok := raw.Clusters[selected.Cluster]
	if !ok || cluster.Server != o.expectedServer || cluster.InsecureSkipTLSVerify || cluster.ProxyURL != "" {
		return nil, errors.New("cluster endpoint or TLS policy does not match")
	}
	auth, ok := raw.AuthInfos[selected.AuthInfo]
	if !ok || auth.Exec != nil || auth.AuthProvider != nil || auth.Impersonate != "" {
		return nil, errors.New("use explicit static disposable credentials without plugins or impersonation")
	}
	overrides := &clientcmd.ConfigOverrides{CurrentContext: o.contextName}
	clientConfig := clientcmd.NewNonInteractiveClientConfig(*raw, o.contextName, overrides, nil)
	cfg, err := clientConfig.ClientConfig()
	if err != nil {
		return nil, errors.New("cannot construct the explicitly selected client configuration")
	}
	cfg.Timeout = 5 * time.Second
	cfg.QPS = 2
	cfg.Burst = 2
	cfg.UserAgent = "ds60-owned-pod-reader"
	// A deliberately selected local teaching target must not inherit a host proxy.
	cfg.Proxy = func(*http.Request) (*url.URL, error) { return nil, nil }
	return cfg, nil
}

func listNames(ctx context.Context, client corev1.CoreV1Interface, namespace string) ([]string, error) {
	names := []string{}
	token := ""
	for page := 0; page < 3; page++ {
		result, err := client.Pods(namespace).List(ctx, metav1.ListOptions{Limit: 20, Continue: token})
		if err != nil {
			return nil, fmt.Errorf("list pods: %w", err)
		}
		for _, pod := range result.Items {
			names = append(names, pod.Name)
			if len(names) > 60 {
				return nil, errors.New("response exceeded the 60-object teaching budget")
			}
		}
		if result.Continue == "" {
			return names, nil
		}
		token = result.Continue
	}
	return nil, errors.New("pagination exceeded the three-page teaching budget")
}

func run(args []string) error {
	f := flag.NewFlagSet("owned-pod-reader", flag.ContinueOnError)
	var o options
	f.StringVar(&o.config, "kubeconfig", "", "explicit disposable target configuration")
	f.StringVar(&o.contextName, "context", "", "explicit context name")
	f.StringVar(&o.namespace, "namespace", "", "explicit owned lesson namespace")
	f.StringVar(&o.expectedServer, "expected-server", "", "exact expected HTTPS API endpoint")
	f.BoolVar(&o.execute, "execute", false, "perform the explicitly configured read-only request")
	if err := f.Parse(args); err != nil {
		return err
	}
	if len(f.Args()) != 0 {
		return errors.New("unexpected positional arguments")
	}
	cfg, err := checkedConfig(o)
	if err != nil {
		return err
	}
	client, err := corev1.NewForConfig(cfg)
	if err != nil {
		return errors.New("cannot construct the typed core client")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	names, err := listNames(ctx, client, o.namespace)
	if err != nil {
		return err
	}
	for _, name := range names {
		fmt.Println(name)
	}
	fmt.Printf("Observed %d pods in the explicitly selected namespace.\n", len(names))
	return nil
}

func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
