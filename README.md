# Overview
Pytorch project as an experiment in model based reinforcement learning.

## Model Example
<p align="center">
  <figure>
  <img src="gif/model.gif?style=centerme">
  </figure>
</p>

## Policy Example
<p align="center">
  <figure>
  <img src="gif/policy.gif?style=centerme">
  </figure>
</p>

# Description 
This experiment isn't reinforcement learning in the strictest sense as the process for training a policy was:
1.  Train model via random inputs and initial conditions in the world.
2.  Train policy back propogating through model using random initial conditions and random targets.

So it is effectively just supervised learning with a simulator.
The component of most interest was whether a policy could be trained by backpropogating through a complex model.  The answer seems to be yes although to be fair the learned policy is only simple and it doesn't have to plan over a long horizon.

The world is a simple physics simulator in numpy.  It contains a block moving in a fixed square space where the velocity reverses on impact with a wall (bounce).  Forces can be applied at each time step.
So essentially the block can be moved to a target location by applying the right forces to guide it there.

The model operates on sets of 4 frames rather than each frame so each timestep is considered as 4 frames.  The justification here then is the frames makeup a Markov state and time only needs to be considered in the context of planning.
If we consider t0 to be the first 4 frames and t1 to be the next 4 frames the aim of model is to predict the next 4 frames at t1.

Similarly the forces are held constant for each timestep of 4 frames.  The model is given the forces for t0 and t1 however it probably only really needs the forces for t1 for an accurate prediction since the forces for t0 could be derived from the t0 frames.

The most interesting component of the model is the Recurrent layer.  The thinking behind this is that while 4 frames capture the state nicely it will not always be possible to reach the target in 1 timestep.  The force is limited and the velocity may be initialized to move away from the target.  So the model needs to "plan" or there will be no gradient for the policy to follow in order to move the block to the target. Due to the number of layers involved just for convolution and deconvolution an LSTM model was used since when looking into the future and backpropogating into the policy the gradients will have to flow through many layers even though there aren't necessarily many long term dependencies in this model. 

## Model Architecture
<p align="center">
  <figure>
  <img src="images/Model.svg">
  <figcaption>Model Architecture</figcaption>
  </figure>
</p>

## Policy Architecture
<p align="center">
  <figure>
  <img src="images/Policy.svg">
  </figure>
</p>
Pre-trained models included with the project.

# Local Installation for testing
Run: `make install`

# Using Pre-trained models
This project includes the pre-trained pytorch modules for model and policy as well as some scripts for testing and interacting with the models.

## Run interactive Demo with Pretrained model
Generates frames using the model open-loop by feeding back the models own output into the model so error increases on time.
`make draw_test_policy`

## Generate test model frames
Generates frames using the model open-loop by feeding back the models own output into the model so error increases on time.
`make clean`
`make draw_test_policy`

## Generate test policy frames
Generates frames using the model and policy by feeding the simulator output into the policy and model.
`make clean`
`make draw_test_policy`

# Setting up kubernetes project
Requires a Google cloud account.
1.  Setup Google Kubernetes Engine project and create a new cluster (It doesn't matter what nodes are there just delete them afterwards).
2.  Create a file in the root directory called GKE_PROJECT.  Inside the file insert the GKE Project name.
3.  Create a file in the root directory called GKE_ClUSTER.  Inside the file insert the GKE CLUSTER name.
4.  run `bash setup_gke` to bind kubectl to this cluster. 
5.  run `bash setup_model_storage.sh` to add a storage bucket used for the models to the project. 
6.  run `bash setup_kubeflow` to install kubeflow into your cluster.
Your kubernetes environment should now be ready to train the model once the node pools are created.

# Training locally
Requires Google Cloud storage to load / save model and policy.
To train the model run:
`bash start_model.sh`
To train the policy run:
`bash start_policy.sh`

# Training on GKE 
1. Run: `bash setup_nodepool_gpu.sh` or `bash setup_nodepool_cpu.sh` to train on gpu (strongly recommended due to 30x performance increase) or cpu respectively.
2. Run: `make push_image_gke` to push the image and push to google docker registry.  It uses the git commit as the
version and updates the kubernetes yaml jobs accordingly.
3. Run: `kubectl create -f kube_train_model_<DEVICE>.yaml` or `kubectl create -f kube_train_policy_<DEVICE>.yaml` to train the model or policy respectively where DEVICE=gpu or cpu.
4. Once training is done run `bash cleanup_nodepool.sh` to decommission the nodes to avoid paying for them any longer than necessary. 
