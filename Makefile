export VERSION := $(shell git rev-parse HEAD)
export GKE_PROJECT := $(shell cat GKE_PROJECT)
export MPC_IMAGE := gcr.io\/$(GKE_PROJECT)\/model_predictive_control_test:$(VERSION)
export KUBE_YAML_IMAGE_INDENT := \ \ \ \ \ \ \ \ \ \ 

install:
	mkdir frames
	pip3 install -r requirements.txt

clean:
	rm frames/*

train_model:
	python3 src/main/python/train_model.py

train_policy:
	python3 src/main/python/train_policy.py

run_model_show_frames:
	python3 src/main/python/run_model_show_frames.py

run_policy_show_frames:
	python3 src/main/python/run_policy_show_frames.py

draw_test_policy:
	python3 src/main/python/draw_test_v2.py

build_image:
	docker build . -t model_predictive_control_test:$(VERSION)

update_deployment_version:
	cat kube_train_model_gpu.yaml | sed 's/^.*- image:.*$$/$(KUBE_YAML_IMAGE_INDENT)- image: $(MPC_IMAGE)/' > kube_train_model_gpu.yaml.bak
	mv kube_train_model_gpu.yaml.bak kube_train_model_gpu.yaml
	cat kube_train_model_cpu.yaml | sed 's/^.*- image:.*$$/$(KUBE_YAML_IMAGE_INDENT)- image: $(MPC_IMAGE)/' > kube_train_model_cpu.yaml.bak
	mv kube_train_model_cpu.yaml.bak kube_train_model_cpu.yaml
	cat kube_train_policy_gpu.yaml | sed 's/^.*- image:.*$$/$(KUBE_YAML_IMAGE_INDENT)- image: $(MPC_IMAGE)/' > kube_train_policy_gpu.yaml.bak
	mv kube_train_policy_gpu.yaml.bak kube_train_policy_gpu.yaml
	cat kube_train_policy_cpu.yaml | sed 's/^.*- image:.*$$/$(KUBE_YAML_IMAGE_INDENT)- image: $(MPC_IMAGE)/' > kube_train_policy_cpu.yaml.bak
	mv kube_train_policy_cpu.yaml.bak kube_train_policy_cpu.yaml

push_image_gke: build_image update_deployment_version
	docker tag model_predictive_control_test:$(VERSION) gcr.io/$(GKE_PROJECT)/model_predictive_control_test:$(VERSION)
	docker push gcr.io/$(GKE_PROJECT)/model_predictive_control_test:$(VERSION)
