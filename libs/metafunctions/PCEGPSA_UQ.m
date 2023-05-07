function out=PCEGPSA_UQ(input)

% This is a function that takes some input/output data and performs a
% sensitivity analysis  using the PCE-GP of UQLab. This function is
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
myInput = uq_createInput(IOpts); % this stores the input info in UQlab (doesn't need to be called again directly)

sopts.Type = 'Metamodel';
sopts.MetaType = 'PCK';
sopts.Mode = 'sequential';
sopts.Input = myInput;
%sopts.FullModel = FULLModel;
sopts.PCE.Method = 'LARS';
sopts.PCE.TruncOptions.qNorm = 0.75;
sopts.PCE.TruncOptions.MaxInteraction=1;
sopts.PCE.Degree = 1:5;
sopts.Kriging.Optim.MaxIter = 50; % max iterations for optimisation of hyperparameters
sopts.Kriging.Corr.Family = 'matern-3_2';
sopts.Kriging.Corr.Type = 'ellipsoidal';
sopts.ExpDesign.Sampling='User';
sopts.ExpDesign.X=X;
sopts.ExpDesign.Y=y;
PCEGPModel = uq_createModel(sopts);

SobolSensOpts.Type = 'Sensitivity';
SobolSensOpts.Method = 'Sobol';
SobolSensOpts.Sobol.SampleSize = 10000; % number of samples of PCEGP to take
SobolSensOpts.SaveEvaluations = false;
SA=uq_createAnalysis(SobolSensOpts);

out.PCEGPModel=PCEGPModel;
out.SA=SA;
out.time=toc(tstart);