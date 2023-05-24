function out=GPSA_UQ(input)

% This is a function that takes some input/output data and performs a
% sensitivity analysis  using the GP of UQLab. This function is
% basically to take default options and make it easy for me to run SA
% through UQLab. Obviously plenty more options and detail available in
% UQLab itself.
%
% Note that here we are taking given X and y data and giving back Si STi,
% etc. So the sampling and model-running are not controlled by UQLab

% Assumes uniform distributions over [0,1]

% So far, just needs X and y as inputs (input.X and input.y). Obviously
% could extend this a lot.

tstart=tic;
uqlab; % open uqlab

X=input.X;
y=input.y;
k=size(X,2);

% define input dists as 0,1 uniform
for ii=1:k
    IOpts.Marginals(ii).Type = 'Uniform' ;
    IOpts.Marginals(ii).Parameters = [0,1] ;
end
myInput = uq_createInput(IOpts); %#ok<NASGU> % this stores the input info in UQlab (doesn't need to be called again directly)

GPOpts.Type='Metamodel';
GPOpts.MetaType='Kriging';
GPOpts.Corr.Type = 'ellipsoidal';
GPOpts.Corr.Family = 'matern-3_2';
GPOpts.Optim.MaxIter = 50; % max iterations for optimisation of hyperparameters
GPOpts.ExpDesign.Sampling='User';
GPOpts.ExpDesign.X=X;
GPOpts.ExpDesign.Y=y;
GPModel = uq_createModel(GPOpts);

SobolSensOpts.Type = 'Sensitivity';
SobolSensOpts.Method = 'Sobol';
SobolSensOpts.Sobol.SampleSize = 10000; % number of samples of GP to take
SobolSensOpts.SaveEvaluations = false;
SA=uq_createAnalysis(SobolSensOpts);

out.GPModel=GPModel;
out.SA=SA;
out.time=toc(tstart);