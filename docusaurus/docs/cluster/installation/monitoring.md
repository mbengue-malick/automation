# Monitoring

- create namespace monitoring `kubectl create ns monitoring`

## Prometheus
- add prometheus-community helm repo `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`
- update helm repos : `helm repo update`
- update values-prometheus.yaml with your own values.
- install prometheus `helm install prometheus-community/kube-prometheus-stack -n monitoring --generate-name --values values-prometheus.yaml`

## Grafana

- one the chart is deployed, you can retrieve admin password using `echo "Password: $(kubectl get secret kube-prometheus-stack-123456789-grafana --namespace monitoring -o jsonpath="{.data.admin-password}" | base64 --decode)"`. (Don't forget to change the name of the secret)
- Go to grafana url and use admin and password credentials to log in.
- Now go to Create > Import and put the ID of the dashboard you want to import, then click on load. A new page will appear, set prometheus as datasource and click on import.

### DCGM Dashboard in Grafana

To add a dashboard for DCGM, you can use a standard dashboard that NVIDIA has made available, which can also be customized.
- To access the dashboard, navigate from the Grafana home page to Dashboards -> Manage -> Import
- Import the NVIDIA dashboard from https://grafana.com/grafana/dashboards/12239 and choose Prometheus as the data source in the drop down.
- The GPU dashboard will now be available on Grafana for visualizing metrics.