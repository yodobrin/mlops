# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. 

import argparse
import os
from azureml.core import Run, Workspace, Datastore, Dataset
from azureml.core.authentication import ServicePrincipalAuthentication

def main(**kwargs):
    # Use the run to log any metrics
    run = Run.get_context()
    for key, value in kwargs.items():
        print ("%s == %s" %(key, value))
        # log it to the run - just showing it
        run.log(key,value)
    input_store_name = kwargs['in_data_store_name']
    path_param = kwargs['path_param1']
    ds_name = kwargs['ds_name']
    tenant = kwargs['tenant']
    client_id = kwargs['client_id']
    client_secret = kwargs['client_secret']
    
    # you must use the spn that was associated with the data store to be able and read from it (in the case the datastore is data-lake gen2)
    sp = ServicePrincipalAuthentication(tenant_id=tenant, 
        service_principal_id=client_id, 
        service_principal_password=client_secret) 
    
    # use your own, workspace name, resource group and subscription id - taken from the config.json
    ws = Workspace.get(name="your-ws-name",
                   auth=sp,
                   resource_group="your-rg-name",
                   subscription_id="your-subscription-id")
    print(ws)

    input_store = Datastore.get(ws,input_store_name)

    my_ds = Dataset.Tabular.from_delimited_files(path = [(input_store, path_param)])
    my_ds.register(workspace,ds_name,'what a description',)


    




# TODO - create a blob somewhere based on the params?



if __name__ == "__main__":
    # Obtain parameters from the calling module
    parser = argparse.ArgumentParser("train")
    # in this case, the pipleline gets 4 parameters, the in/out datastores and the relavant path within each datastore
    parser.add_argument("--in_data_store_name", type=str, help="the name of the input datastore")
    parser.add_argument("--out_data_store_name", type=str, help="the name of the output datastore")
    parser.add_argument("--path_param1", type=str, help="sample path parameter")
    parser.add_argument("--path_param2", type=str, help="sample second path parameter")
    # data store credentials, to be used in the pipeline
    parser.add_argument("--tenant", type=str, help="your tenant")
    parser.add_argument("--client_id", type=str, help="your client id (registered of the data store)")
    parser.add_argument("--client_secret", type=str, help="client secret")
    # data set name
    parser.add_argument("--ds_name", type=str, help="name of the dataset to be created")
    args = parser.parse_args()
    
    main(in_data_store_name=args.in_data_store_name,
        out_data_store_name=None, 
        path_param1=args.path_param1,
        path_param2=args.path_param2,
        ds_name=args.ds_name,
        tenant=args.tenant,
        client_id=args.client_id,
        client_secret=args.client_secret)