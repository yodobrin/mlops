import azureml.core
from azureml.core import Workspace, Experiment
from azureml.core.compute import ComputeTarget, AmlCompute
# from azureml.data.datapath import DataPath, DataPathComputeBinding
# from azureml.widgets import RunDetails

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

# create pipeline string parameters
string_pipeline_1param = PipelineParameter(name="1st_string", default_value='sample_1_string_default_value')
string_pipeline_2param = PipelineParameter(name="2nd_string", default_value='sample_2_string_default_value')

# TODO - add more complicated params, and datapaths

# create pipeline python step
# note the script name must match the main script that needs to run

train_step = PythonScriptStep(
    name='train_step',
    script_name="demo_train.py",
    arguments=["--arg1", string_pipeline_1param, "--arg2", string_pipeline_2param],
    compute_target=compute_target, 
    source_directory=source_directory)




# create the pipeline
pipeline = Pipeline(workspace=ws, steps=[train_step])

# publish the pipeline
published_pipeline = pipeline.publish(name="sample_2nd_pipeline",  description="Sample created from vscode showcasing param passing", version="3.0",continue_on_step_failure=True)

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