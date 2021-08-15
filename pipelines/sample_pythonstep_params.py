import azureml.core
from azureml.core import Workspace, Experiment, Datastore
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.data.datapath import DataPath, DataPathComputeBinding

from azureml.pipeline.core import PipelineParameter
from azureml.pipeline.core import Pipeline, PipelineRun
from azureml.pipeline.steps import PythonScriptStep


def get_published_pipeline(ws,name,version):
    """
    Returns a published pipeline by name and version
    """
    published_pipelines = PublishedPipeline.list(ws)
    for pipe in published_pipelines:        
        p_name = pipe.name
        p_version = pipe.version
        if(p_name == name and p_version is not None and p_version==version):
            return pipe 
        else:
            return None




def create_cluster(ws,number_of_nodes, idle_time_out, cluster_name,vmsize):
    """Create dedicated clusters per the input
    Keyword arguments:
    ws -- the workspace in which compute should be created
    number_of_nodes -- how many (max) nodes in each cluster
    idle_time_out -- idle time of a node before it is recycled 
    cluster_name -- used as the name for the cluster, if the cluster exist, no new cluster will be created
    """
    try:
        compute_target = AmlCompute(workspace=ws, name=cluster_name)        
    except ComputeTargetException:
        compute_config = AmlCompute.provisioning_configuration(vm_size=vmsize,
                                                                max_nodes=number_of_nodes, 
                                                                idle_seconds_before_scaledown=idle_time_out)
        compute_target = AmlCompute.create(ws, cluster_name, compute_config)
        compute_target.wait_for_completion(show_output=True)
        
    return compute_target
# obtain the workspace (ensure config.json is in your path)
ws = Workspace.from_config()
# create or reference the compute the pipeline will use
compute_target = create_cluster(ws,2,120,'dp100','Standard_DS2_v2')
# reference the source directory: where all your files including the main script
source_directory = '../src'

# create pipeline string parameters, input datastore, output datastore (if needed) and path params
input_ds_name = PipelineParameter(name="input_ds_name", default_value='landing')
output_ds_name = PipelineParameter(name="output_ds_name", default_value='landing')
path_param1 = PipelineParameter(name="path_param1", default_value='silver')
path_param2 = PipelineParameter(name="path_param2", default_value='silver')
# data store credentials params to be used by the pipeline
tenant = PipelineParameter(name="tenant", default_value='your tenant')
client_id = PipelineParameter(name="client_id", default_value='your client id - registed of the data store')
client_secret = PipelineParameter(name="client_secret", default_value='your client secret')
# data set name to be created
ds_name = PipelineParameter(name="ds_name", default_value='the name of the registered data set')


# create pipeline python step
# note the script name must match the main script that needs to run

train_step = PythonScriptStep(
    name='a_step',
    script_name="demo_train.py",
    arguments=["--in_data_store_name", input_ds_name, 
        "--out_data_store_name", output_ds_name,
        "--path_param1",path_param1,
        "--path_param2",path_param2,
        "--tenant",tenant,
        "--client_id",client_id,
        "--client_secret",client_secret,
        "--ds_name",ds_name],
    compute_target=compute_target,
    source_directory=source_directory)




# create the pipeline
pipeline = Pipeline(workspace=ws, steps=[train_step])

# publish the pipeline
published_pipeline = pipeline.publish(name="sample_5th_pipeline",  description="data path and arguments", version="1.0",continue_on_step_failure=True)

# lookup a specific pipeline by name and version - to be used in a published endpoint
# p_pipeline = get_published_pipeline(ws,"sample_2nd_pipeline","2.0")
# pipeline_endpoint = PipelineEndpoint.publish(workspace=ws, 
#                                                 name="published_sample_endpoint_2nd", 
#                                                 pipeline=p_pipeline, 
#                                                 description="Test description Notebook")

# After the first publish, any changes to the end-point is not done via the publish command, rather add, or add_default
# So to add another version to an end-point, you will need to
# 1. get reference to the deserired pipeline (it needs to be with a diffrent id - meaning another pipeline)
# 2. get the end_point
# 3. add the new pipeline - note that adding is not setting it as the default version, rather it increments the version
# 4. optional - set the new version as the default

# The follwing code is commented out, use as you see fit
# p_pipeline = get_published_pipeline(ws,"sample_2nd_pipeline","3.0")
# pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name="published_sample_endpoint_2nd")
# pipeline_endpoint.add(p_pipeline)
# pipeline_endpoint.set_default_version('1')